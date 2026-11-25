/* Pulse is an additive UI layer: timetable, search, sharing and native hooks stay intact. */
(function() {
  'use strict';
  let profile = PulseProfile.read(localStorage), draft, step = 0, dialog, returnFocus;
  const mark = '<img class="pulse-mark" src="pulse-mark.png" alt="">';
  const roleName = p => p.role === 'student' ? 'Студент' : p.curator ? 'Преподаватель · куратор' : 'Преподаватель';
  const groups = campus => (state.data?.groups || []).filter(g => (g.source || 'spk') === campus);
  const choices = () => draft.role === 'student' || step === 3 ? groups(draft.campus) : TeacherIndex.build({groups: groups(draft.campus)});
  function personal() {
    return profile && state.campus === profile.campus && (profile.role === 'student'
      ? state.page === 'schedule' && state.group === profile.id
      : state.page === 'teachers' && state.teacher === profile.id && !state.teacherSelecting);
  }
  function home() {
    if (!profile) { openProfile(); return; }
    state.campus = profile.campus;
    indexCampus();
    if (profile.role === 'student') {
      state.group = profile.id; state.page = 'schedule'; state.campusGroups[profile.campus] = profile.id;
    } else { state.teacher = profile.id; state.teacherSelecting = false; state.page = 'teachers'; }
    persist(false); render('page');
  }
  function intro() {
    if (!personal()) return '';
    let html = '<section class="pulse-intro"><div><div class="eyebrow">'+esc(roleName(profile))+'</div><h2>Твой день. Твой ритм.</h2><p>Всё важное — в одном расписании.</p></div><button class="icon-button" data-pulse="profile" aria-label="Изменить профиль">'+icon('user')+'</button></section>';
    if (profile.curator) html += '<section class="pulse-curator" aria-label="Курируемые группы"><div class="pulse-section-title"><h2>Мои группы</h2><button class="text-button" data-pulse="profile">Изменить</button></div><div class="pulse-group-strip">'+profile.groups.map(id => {
      const g = state.data.groups.find(item => item.id === id);
      if (!g) return '<div class="pulse-group-chip"><strong>'+esc(id)+'</strong><small>Нет в текущей таблице</small></div>';
      const count = (g.weeks?.[parity()]?.[state.day] || []).length;
      return '<button class="pulse-group-chip" data-group="'+esc(id)+'"><small>'+(g.source === 'crk' ? 'ЦРК' : 'СПК')+'</small><strong>'+esc(g.name)+'</strong><span>'+count+' пар в выбранный день '+icon('arrow')+'</span></button>';
    }).join('')+'</div></section>';
    return html;
  }
  const schedule = renderSchedule, teachers = renderTeachers, settings = renderSettings;
  function decorate(html) {
    const heading = intro();
    return html.includes('<div class="timetable-controls">')
      ? html.replace('<div class="timetable-controls">', '<div class="timetable-controls">'+heading)
      : heading + html;
  }
  renderSchedule = function() { return decorate(schedule()); };
  renderTeachers = function() { return decorate(teachers()); };
  renderSettings = function() {
    return '<section class="pulse-profile-card">'+mark+'<div><h2>Твой Pulse</h2><p>'+esc(profile ? roleName(profile) : 'Настройте личное расписание')+'</p></div><button class="text-button" data-pulse="profile">Изменить профиль</button></section>'+settings();
  };
  const renderBase = render;
  render = function(motion = '') {
    renderBase(motion);
    for (const [action, page] of [['choose','schedule'],['teachers-choose','teachers']]) {
      const tab = document.querySelector('.bottom-nav [data-action="'+action+'"]');
      const active = !personal() && state.page === page;
      tab?.classList.toggle('active', active);
      if (active) tab?.setAttribute('aria-current','page'); else tab?.removeAttribute('aria-current');
    }
    const button = document.querySelector('[data-pulse="home"]');
    if (button) {
      button.classList.toggle('active', !!personal());
      if (personal()) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
      if (personal()) document.querySelectorAll('.bottom-nav [data-page]').forEach(item => {
        item.classList.remove('active'); item.removeAttribute('aria-current');
      });
    }
  };
  function openProfile() {
    if (dialog?.open) return;
    returnFocus = document.activeElement;
    draft = profile ? {...profile, groups: [...profile.groups]} : {version: 2, role: 'student', campus: state.campus, id: '', curator: false, groups: []};
    step = 0;
    dialog = document.createElement('dialog');
    dialog.className = 'pulse-onboarding';
    dialog.setAttribute('aria-labelledby', 'pulseTitle');
    dialog.addEventListener('cancel', e => { e.preventDefault(); closeProfile(); });
    dialog.addEventListener('click', handleWizardClick);
    dialog.addEventListener('input', e => { if (e.target.id === 'pulseSearch') fillChoices(e.target.value); });
    dialog.addEventListener('change', e => {
      if (e.target.name !== 'pulseChoice') return;
      if (step === 3) {
        draft.groups = e.target.checked ? [...new Set([...draft.groups, e.target.value])] : draft.groups.filter(id => id !== e.target.value);
      } else draft.id = e.target.value;
      updateNext();
    });
    document.body.appendChild(dialog); drawStep(); dialog.showModal();
    dialog.querySelector('h1').focus();
  }
  function closeProfile() {
    dialog.close(); dialog.remove(); dialog = null;
    returnFocus?.focus?.({preventScroll: true});
  }
  function drawStep() {
    const titles = ['В своём ритме.', draft.role === 'student' ? 'Какая у тебя группа?' : 'Найдём ваше расписание.', 'Вы куратор группы?', 'Ваши группы. Рядом.'];
    const subtitles = ['Pulse подстроит главный экран под тебя.', 'Выберите запись из расписания колледжа.', 'Добавим быстрый доступ к расписанию ваших групп.', 'Можно выбрать несколько групп из СПК и ЦРК.'];
    dialog.innerHTML = '<div class="pulse-wizard-top">'+mark+'<span>Pulse <small>2.0</small></span><button class="icon-button" data-wizard="close" aria-label="Настроить позже">'+icon('close')+'</button></div><div class="pulse-progress" aria-label="Шаг '+(step+1)+' из '+(draft.role === 'student' ? 2 : 4)+'">'+[0,1,2,3].slice(0,draft.role === 'student' ? 2 : 4).map(n => '<i class="'+(n <= step ? 'done' : '')+'"></i>').join('')+'</div><h1 id="pulseTitle" tabindex="-1">'+titles[step]+'</h1><p class="pulse-subtitle">'+subtitles[step]+'</p><div class="pulse-step-body"></div><p id="pulseError" role="alert"></p><footer class="pulse-wizard-footer"><button class="text-button" data-wizard="back">'+(step ? 'Назад' : 'Позже')+'</button><button class="button-primary" id="pulseNext" data-wizard="next">'+(step === 3 || step === 1 && draft.role === 'student' ? 'Открыть Pulse' : 'Продолжить')+' '+icon('arrow')+'</button></footer>';
    const body = dialog.querySelector('.pulse-step-body');
    if (step === 0) body.innerHTML = '<div class="pulse-role-options">'+[['student','book','Я студент','Пары, кабинеты и любимые предметы.'],['teacher','user','Я преподаватель','Занятия, группы и кураторство.']].map(([id,ic,title,copy]) => '<button class="pulse-role" data-role="'+id+'" aria-pressed="'+(draft.role === id)+'">'+icon(ic)+'<strong>'+title+'</strong><span>'+copy+'</span>'+icon('arrow')+'</button>').join('')+'</div>';
    else if (step === 2) body.innerHTML = '<div class="pulse-role-options">'+[[true,'Да, я куратор','Выберу курируемые группы'],[false,'Нет, только занятия','Моё расписание преподавателя']].map(([yes,title,copy]) => '<button class="pulse-role" data-curator="'+yes+'" aria-pressed="'+(draft.curator === yes)+'"><strong>'+title+'</strong><span>'+copy+'</span></button>').join('')+'</div>';
    else {
      body.innerHTML = '<div class="pulse-campus" role="group" aria-label="Источник расписания">'+['spk','crk'].map(c => '<button data-pulse-campus="'+c+'" aria-pressed="'+(draft.campus === c)+'">'+(c === 'spk' ? 'СПК' : 'ЦРК')+'</button>').join('')+'</div><label class="pulse-search-label" for="pulseSearch">'+(step === 3 || draft.role === 'student' ? 'Найти группу' : 'Фамилия преподавателя')+'</label><input id="pulseSearch" type="search" autocomplete="off" placeholder="Начните вводить…"><div id="pulseChoices" class="pulse-choices"></div><p id="pulseSelection" aria-live="polite"></p>';
      fillChoices('');
    }
    updateNext();
  }
  function fillChoices(query) {
    const list = choices().filter(item => item.name.toLocaleLowerCase('ru').includes(query.trim().toLocaleLowerCase('ru')));
    const box = dialog.querySelector('#pulseChoices');
    box.innerHTML = list.length ? list.map(item => '<label class="pulse-choice"><input name="pulseChoice" type="'+(step === 3 ? 'checkbox' : 'radio')+'" value="'+esc(item.id)+'" '+((step === 3 ? draft.groups.includes(item.id) : draft.id === item.id) ? 'checked' : '')+'><span>'+esc(item.name)+'</span>'+icon('check')+'</label>').join('') : '<p class="pulse-no-results">'+(state.data ? 'Ничего не найдено. Попробуйте другой запрос или источник.' : 'Расписание ещё загружается. Закройте настройку и повторите загрузку.')+'</p>';
  }
  function updateNext() {
    const next = dialog.querySelector('#pulseNext');
    next.disabled = step === 1 ? !choices().some(x => x.id === draft.id) : step === 3 ? !draft.groups.length : false;
    const count = dialog.querySelector('#pulseSelection');
    if (count) count.textContent = step === 3 ? 'Выбрано групп: '+draft.groups.length : draft.id ? 'Выбор сохранён для этого шага' : 'Выберите одну запись';
  }
  function finish() {
    try {
      // The identity source is fixed at step 1; curated groups may span sources.
      profile = PulseProfile.save(localStorage, {...draft, campus: draft.identityCampus || draft.campus});
      closeProfile(); home();
    } catch (error) { dialog.querySelector('#pulseError').textContent = 'Не удалось сохранить профиль. '+error.message; }
  }
  function handleWizardClick(event) {
    const b = event.target.closest('button'); if (!b || b.disabled) return;
    if (b.dataset.role) {
      if (draft.role !== b.dataset.role) { draft.role = b.dataset.role; draft.id = ''; draft.curator = false; draft.groups = []; }
      drawStep();
    } else if (b.dataset.curator) { draft.curator = b.dataset.curator === 'true'; drawStep(); }
    else if (b.dataset.pulseCampus) {
      if (draft.campus === b.dataset.pulseCampus) return;
      draft.campus = b.dataset.pulseCampus; if (step === 1) draft.id = ''; drawStep();
    } else if (b.dataset.wizard === 'close' || b.dataset.wizard === 'back' && step === 0) closeProfile();
    else if (b.dataset.wizard === 'back') {
      step--; if (step === 1) draft.campus = draft.identityCampus || draft.campus; drawStep();
    } else if (b.dataset.wizard === 'next') {
      if (step === 1) draft.identityCampus = draft.campus;
      if (step === 3 || step === 1 && draft.role === 'student' || step === 2 && !draft.curator) finish();
      else { step++; drawStep(); dialog.querySelector('h1').focus(); }
    }
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('[data-pulse]'); if (!b) return;
    if (b.dataset.pulse === 'home') home(); else if (b.dataset.pulse === 'profile') openProfile();
  });
  const oldBack = window.handleBack;
  window.handleBack = function() { if (dialog?.open) { if (step) { step--; drawStep(); } else closeProfile(); return true; } return oldBack(); };
  let first = true;
  const receive = window.onScheduleData;
  window.onScheduleData = function(data) {
    receive(data);
    if (!state.data) return;
    if (first) {
      first = false;
      // Preserve explicit shared schedule destinations; web.js handles them after this callback.
      if (profile && !location.search) home();
      else if (!profile && !location.search) openProfile();
    } else if (dialog?.open && (step === 1 || step === 3)) { fillChoices(dialog.querySelector('#pulseSearch').value); updateNext(); }
  };
  if (!saved.theme && !profile) { state.theme = 'dark'; applyTheme(); }
  document.documentElement.classList.add('pulse-ready');
  $('navCrk').innerHTML = icon('book');
  if (state.data) window.onScheduleData(state.data);
})();

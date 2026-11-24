/* Versioned profile, independent of existing preferences and favorites. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PulseProfile = api;
})(typeof window === 'undefined' ? globalThis : window, function() {
  'use strict';
  const KEY = 'pulse.profile.v2';
  function normalize(value) {
    if (!value || value.version !== 2 || !['student', 'teacher'].includes(value.role)) return null;
    const role = value.role, campus = value.campus === 'crk' ? 'crk' : 'spk';
    const id = typeof value.id === 'string' ? value.id.trim() : '';
    if (!id) return null;
    return {version: 2, role, campus, id, curator: role === 'teacher' && value.curator === true,
      groups: role === 'teacher' && value.curator === true && Array.isArray(value.groups)
        ? [...new Set(value.groups.filter(x => typeof x === 'string' && x.trim()))] : []};
  }
  function read(storage) { try { return normalize(JSON.parse(storage.getItem(KEY))); } catch (_) { return null; } }
  function save(storage, value) {
    const profile = normalize(value);
    if (!profile || (profile.curator && !profile.groups.length)) throw Error('Выберите профиль и курируемые группы.');
    storage.setItem(KEY, JSON.stringify(profile));
    return profile;
  }
  return {KEY, normalize, read, save};
});

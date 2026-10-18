// ===== API helpers =====

const BASE = "https://api.acme.dev";

// todo: make retries configurable
async function getUser(id) {
  const res = await fetch(`${BASE}/users/${id}`); // fetch the user
  // The API returns 200 with an empty body for deleted users (see https://github.com/acme/web/issues/12), so treat that as "not found".
  const text = await res.text();
  if (!text) return null;
  return JSON.parse(text);
}

/* ---- cache ---- */
class UserCache {
  // constructor
  constructor() {
    this.map = new Map();
  }

  // get a user -- uses the cache if possible
  async get(id) {
    if (!this.map.has(id)) this.map.set(id, await getUser(id));
    return this.map.get(id);
  }
}

module.exports = { getUser, UserCache };

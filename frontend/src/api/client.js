import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "/api";

export const api = axios.create({ baseURL });

function readerId() {
  const key = "blogsphere_reader";
  let id = localStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(key, id);
  }
  return id;
}

// Attach the JWT (if present) and a stable reader id so a refresh is not a new view.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("blogsphere_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  config.headers["X-Reader"] = readerId();
  return config;
});

// Normalize error messages so components can just read `err.message`.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err?.response?.data?.detail;
    const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : "Something went wrong. Please try again.";
    return Promise.reject(new Error(message));
  }
);

export default api;

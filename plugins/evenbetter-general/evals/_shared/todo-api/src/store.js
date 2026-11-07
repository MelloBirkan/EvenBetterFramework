// In-memory todo store. Swapped for a database in production.
let nextId = 1;
const todos = new Map();

export function listTodos() {
  return [...todos.values()];
}

export function createTodo(title) {
  const todo = { id: nextId++, title, done: false, createdAt: new Date().toISOString() };
  todos.set(todo.id, todo);
  return todo;
}

export function updateTodo(id, changes) {
  const todo = todos.get(id);
  if (!todo) return null;
  Object.assign(todo, changes);
  return todo;
}

export function deleteTodo(id) {
  return todos.delete(id);
}

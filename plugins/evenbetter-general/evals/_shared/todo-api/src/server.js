import express from "express";
import { listTodos, createTodo, updateTodo, deleteTodo } from "./store.js";

const app = express();
app.use(express.json());

app.get("/todos", (req, res) => {
  res.json(listTodos());
});

app.post("/todos", (req, res) => {
  const { title } = req.body ?? {};
  if (typeof title !== "string" || !title.trim()) {
    return res.status(400).json({ error: "title is required" });
  }
  res.status(201).json(createTodo(title.trim()));
});

app.patch("/todos/:id", (req, res) => {
  const { title, done } = req.body ?? {};
  const todo = updateTodo(Number(req.params.id), {
    ...(typeof title === "string" ? { title } : {}),
    ...(typeof done === "boolean" ? { done } : {}),
  });
  if (!todo) return res.status(404).json({ error: "not found" });
  res.json(todo);
});

app.delete("/todos/:id", (req, res) => {
  if (!deleteTodo(Number(req.params.id))) return res.status(404).json({ error: "not found" });
  res.status(204).end();
});

app.listen(process.env.PORT ?? 3000);

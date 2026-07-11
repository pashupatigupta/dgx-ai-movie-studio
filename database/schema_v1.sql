-- ==========================================
-- DGX AI Movie Studio Database Schema
-- ==========================================

-------------------------------------------------
-- Projects
-------------------------------------------------

CREATE TABLE IF NOT EXISTS projects (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-------------------------------------------------
-- Prompt Library
-------------------------------------------------

CREATE TABLE IF NOT EXISTS prompts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT,

    prompt TEXT,

    negative_prompt TEXT,

    model TEXT,

    seed INTEGER,

    width INTEGER,

    height INTEGER,

    steps INTEGER,

    cfg REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-------------------------------------------------
-- Generated Images
-------------------------------------------------

CREATE TABLE IF NOT EXISTS images (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    project_id INTEGER,

    filename TEXT,

    filepath TEXT,

    prompt TEXT,

    negative_prompt TEXT,

    checkpoint TEXT,

    width INTEGER,

    height INTEGER,

    steps INTEGER,

    cfg REAL,

    seed INTEGER,

    generation_time REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(project_id) REFERENCES projects(id)

);

------------------------
CREATE TABLE IF NOT EXISTS prompts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    category TEXT,

    prompt TEXT NOT NULL,

    negative_prompt TEXT,

    favorite INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
-------------------------------------------------
-- Models
-------------------------------------------------

CREATE TABLE IF NOT EXISTS models (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    model_name TEXT,

    model_type TEXT,

    checkpoint TEXT,

    status TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-------------------------------------------------
-- GPU Benchmark
-------------------------------------------------

CREATE TABLE IF NOT EXISTS benchmark (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    model TEXT,

    gpu_name TEXT,

    gpu_memory REAL,

    generation_time REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-------------------------------------------------
-- Settings
-------------------------------------------------

CREATE TABLE IF NOT EXISTS settings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    setting_name TEXT UNIQUE,

    setting_value TEXT

);

# DroidRun-CampusSync
An autonomous Android agent built with DroidRun and Gemini 2.5 Flash. Reads WhatsApp schedules and auto-syncs them to Calendar &amp; Alarms.

> **Droidrun DevSprint 2026 Submission | IIT Patna**
> *Automating student life with DroidRun & Gemini 2.5 Flash*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Framework-DroidRun-orange)
![AI Model](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-green)

## 📖 Overview
**CampusSync** is an autonomous Android agent designed to ensure you never miss a class again. Instead of manually checking WhatsApp groups for schedule updates, CampusSync uses **Google Gemini 2.5** to "read" your chats, understand the context, and automatically configure your phone's Calendar and Alarms.

This project demonstrates the power of **On-Device Agentic Workflow** using the DroidRun framework.

## 🚀 Key Features
* **🤖 Smart Chat Parsing:** Reads natural language messages from WhatsApp (e.g., *"Physics Class tomorrow at 2 PM"*) and extracts actionable data.
* **📅 Auto-Scheduling:** Automatically opens Google Calendar and creates detailed events.
* **⏰ Smart Alarms:** Sets alarms 30 minutes before class to ensure punctuality.
* **📱 Autonomous Navigation:** Uses DroidRun to navigate the Android UI, type, and scroll just like a human user.

## 🛠️ Tech Stack
* **Core Framework:** [DroidRun](https://github.com/droidrun/droidrun) (for Android UI control)
* **Intelligence:** Google Gemini 2.5 Flash (via `google-genai` SDK)
* **Connectivity:** ADB (Android Debug Bridge)
* **Language:** Python 3.10+

---

## ⚙️ Setup & Installation

### 1. Prerequisites
* Python 3.10 or higher installed.
* An Android Device or Emulator (with Developer Options & USB Debugging enabled).
* A Google Cloud API Key (with access to Gemini models).

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/CampusSync.git](https://github.com/YOUR_USERNAME/CampusSync.git)
cd CampusSync

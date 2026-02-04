# 📱 CampusSync: AI-Powered Academic Assistant

> **From WhatsApp to Reality.** A neuro-symbolic AI agent that automates your academic schedule by reading class updates from WhatsApp and syncing them to your Calendar & Alarm clock instantly.

[![Docker Build](https://img.shields.io/badge/Docker-Production%20Ready-blue?logo=docker)](https://hub.docker.com/) 
[![Python 3.11](https://img.shields.io/badge/Python-3.11-yellow?logo=python)](https://python.org) 
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini Pro](https://img.shields.io/badge/AI-Gemini%20Pro-orange?logo=google)](https://deepmind.google/technologies/gemini/)

---

## 🎥 Demo Video
*[Link to your YouTube/Drive Demo Video goes here]*

---

## 🧐 The Problem
Students today manage their academic lives through chaos.
* **Critical Info is Unstructured:** "Class rescheduled to 10 AM" messages are buried in WhatsApp groups.
* **Manual Friction:** Students forget to set alarms or update calendars manually.
* **The Result:** Missed lectures, late submissions, and academic stress.

## 💡 The Solution: CampusSync
CampusSync is an **autonomous agent** that bridges the gap between unstructured chat data and structured mobile actions.
1.  **Reads** messages from specific WhatsApp groups using Accessibility APIs (via DroidRun).
2.  **Understands** context (Date, Time, Course Code) using **Google Gemini Pro**.
3.  **Acts** by autonomously navigating the Android UI to set Alarms and Calendar events—just like a human would.

---

## 🏗️ Cloud-Native Architecture (The "Brain & Body" Model)

We designed CampusSync with a **Cloud-Native Architecture** that decouples the intelligence from the hardware. This allows one central "Brain" to control any "Body" (device) anywhere in the world.

```mermaid
graph TD
    %% Define Nodes with Quotes
    User(["👤 User Dashboard"])
    
    %% Note the QUOTES inside the brackets below
    subgraph Brain ["🐳 The Brain (Docker Container)"]
        direction TB
        FastAPI["⚡ FastAPI Server"]
        Agent["🤖 DroidRun Agent"]
        Gemini["🧠 Gemini Pro API"]
    end
    
    subgraph Body ["📱 The Body (Android Device)"]
        direction TB
        WhatsApp["💬 WhatsApp"]
        Actions["📅 Calendar & Alarm"]
    end

    %% Define Connections
    User -->|1. Trigger Sync| FastAPI
    FastAPI --> Agent
    Agent <-->|2. Analyze Context| Gemini
    Agent ==>|3. ADB Bridge TCP/IP| WhatsApp
    Agent ==>|4. Automate UI| Actions

# 🤖 Smart Task Manager Agent with Auto & Manual Reminders

A powerful AI-assisted Smart Task Manager built with **Streamlit** that helps users efficiently manage tasks, set reminders, and receive **automatic sound alerts** before deadlines — using background threading, JSON-based persistence, and real-time monitoring.

---

## 🌟 Features

🔹 Create tasks with title, description, due time, priority, and category  
🔹 Automatic reminders **30 minutes before due time**  
🔹 Manual reminder scheduling (user-defined time)  
🔊 **Sound notifications** using winsound (Windows) or system beep  
⏳ Real-time countdown tracking for all pending tasks  
📁 Auto storage in `tasks.json` (persistent across sessions)  
⏳ Quick task creation (due in 5–120 mins)  
⏱ Reminder Service runs **in background using threading**  
📤 Export task status report (future enhancement)

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | Python 3 |
| Task Persistence | JSON File |
| Notification | winsound / system beep |
| Date/time management | datetime, timedelta |
| Background Service | Threading |
| UI | Streamlit Widgets & Containers |

 --- 
## 📂 Project Structure
Task-Manager-Agent/
│── app.py
│── README.md
│── requirements.txt
│── architecture_diagram.png (optional)
│── tasks.json

---

## 🚀 Installation & Run

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt

streamlit run task_scheduler.py --server.port 5000 --server.address 127.0.0.1

```
Flow/Architecture Diagram and demo video has been uploaded

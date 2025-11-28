import streamlit as st
import pandas as pd
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict
import os
import platform
# Only import winsound if running on Windows
if platform.system() == "Windows":
    import winsound
class TaskManagerAgent:
    def __init__(self):
        self.tasks_file = "tasks.json"
        self.tasks = self.load_tasks()
        self.reminder_thread = None
        self.running = False
        
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r') as f:
                    tasks = json.load(f)
                    # Convert string dates back to datetime objects
                    for task in tasks:
                        task['created_at'] = datetime.fromisoformat(task['created_at'])
                        if task['due_date']:
                            task['due_date'] = datetime.fromisoformat(task['due_date'])
                        if task['completed_at']:
                            task['completed_at'] = datetime.fromisoformat(task['completed_at'])
                        if task.get('manual_reminder_time'):
                            task['manual_reminder_time'] = datetime.fromisoformat(task['manual_reminder_time'])
                    return tasks
        except Exception as e:
            print(f"Error loading tasks: {e}")
        return []
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            tasks_to_save = []
            for task in self.tasks:
                task_copy = task.copy()
                task_copy['created_at'] = task['created_at'].isoformat()
                task_copy['due_date'] = task['due_date'].isoformat() if task['due_date'] else None
                task_copy['completed_at'] = task['completed_at'].isoformat() if task['completed_at'] else None
                task_copy['manual_reminder_time'] = task.get('manual_reminder_time').isoformat() if task.get('manual_reminder_time') else None
                tasks_to_save.append(task_copy)
            
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks_to_save, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def create_task(self, title: str, description: str, due_date: datetime, 
                   priority: str = "Medium", category: str = "General",
                   manual_reminder_minutes: int = 0) -> str:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1}_{int(time.time())}"
        
        # Calculate manual reminder time if specified
        manual_reminder_time = None
        if manual_reminder_minutes > 0:
            manual_reminder_time = due_date - timedelta(minutes=manual_reminder_minutes)
        
        task = {
            'id': task_id,
            'title': title,
            'description': description,
            'due_date': due_date,
            'priority': priority,
            'category': category,
            'status': 'pending',  # pending, completed
            'created_at': datetime.now(),
            'completed_at': None,
            'reminders_sent': 0,
            'last_reminder_sent': None,
            'manual_reminder_time': manual_reminder_time,
            'manual_reminder_sent': False
        }
        
        self.tasks.append(task)
        self.save_tasks()
        print(f"✅ Task created: {title} (ID: {task_id})")
        return task_id
    
    def play_reminder_sound(self):
        """Play sound notification for reminders"""
        try:
            if platform.system() == "Windows":
                # Play alert sound (frequency, duration)
                winsound.Beep(1000, 1000)  # 1000Hz for 1 second
                time.sleep(0.5)
                winsound.Beep(1000, 1000)  # Second beep
            else:
                # For Mac/Linux - system beep
                print("\a")  # System bell
        except Exception as e:
            print(f"Could not play sound: {e}")
    
    def mark_task_completed(self, task_id: str):
        """Mark a task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now()
                self.save_tasks()
                print(f"✅ Task completed: {task['title']}")
                return True
        return False
    
    def delete_task(self, task_id: str):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        self.save_tasks()
        print(f"🗑️ Task deleted: {task_id}")
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task['status'] == 'pending']
    
    def get_completed_tasks(self) -> List[Dict]:
        """Get all completed tasks"""
        return [task for task in self.tasks if task['status'] == 'completed']
    
    def get_tasks_due_soon(self, minutes_before: int = 30) -> List[Dict]:
        """Get tasks that are due within the specified minutes"""
        now = datetime.now()
        due_soon = []
        
        for task in self.get_pending_tasks():
            if task['due_date']:
                time_until_due = task['due_date'] - now
                if timedelta(0) <= time_until_due <= timedelta(minutes=minutes_before):
                    due_soon.append(task)
        
        return due_soon
    
    def get_manual_reminders_due(self) -> List[Dict]:
        """Get tasks with manual reminders that are due"""
        now = datetime.now()
        manual_reminders_due = []
        
        for task in self.get_pending_tasks():
            if (task.get('manual_reminder_time') and 
                not task.get('manual_reminder_sent', False) and
                task['manual_reminder_time'] <= now):
                manual_reminders_due.append(task)
        
        return manual_reminders_due
    
    def send_reminder(self, task: Dict, reminder_type: str = "auto"):
        """Send reminder for a task with sound"""
        try:
            # Play sound notification
            self.play_reminder_sound()
            
            # Create reminder message
            time_left = task['due_date'] - datetime.now()
            minutes_left = max(0, int(time_left.total_seconds() / 60))
            
            if reminder_type == "manual":
                reminder_msg = f"🔔 MANUAL REMINDER: '{task['title']}'"
                task['manual_reminder_sent'] = True
            else:
                reminder_msg = f"🔔 REMINDER: '{task['title']}' is due in {minutes_left} minutes!"
            
            # Print to console with visual emphasis
            print("=" * 60)
            print("🚨🚨🚨  TASK REMINDER  🚨🚨🚨")
            print(reminder_msg)
            print(f"Due at: {task['due_date'].strftime('%Y-%m-%d %H:%M')}")
            if task['description']:
                print(f"Description: {task['description']}")
            print("=" * 60)
            
            # Update reminder tracking
            if reminder_type == "auto":
                task['reminders_sent'] += 1
                task['last_reminder_sent'] = datetime.now()
            
            self.save_tasks()
            
            # Store reminder in session state for UI display
            if 'recent_reminders' not in st.session_state:
                st.session_state.recent_reminders = []
            
            st.session_state.recent_reminders.append({
                'task': task['title'],
                'time': datetime.now(),
                'message': reminder_msg,
                'due_time': task['due_date'].strftime('%H:%M'),
                'type': reminder_type,
                'sound_played': True
            })
            
            # Keep only last 10 reminders
            if len(st.session_state.recent_reminders) > 10:
                st.session_state.recent_reminders = st.session_state.recent_reminders[-10:]
            
            return True
        except Exception as e:
            print(f"Error sending reminder: {e}")
            return False
    
    def send_manual_reminder_now(self, task_id: str):
        """Send immediate manual reminder for a task"""
        for task in self.tasks:
            if task['id'] == task_id and task['status'] == 'pending':
                self.send_reminder(task, "manual")
                print(f"✅ Manual reminder sent for: {task['title']}")
                return True
        return False
    
    def start_reminder_service(self):
        """Start the background reminder service"""
        if not self.running:
            self.running = True
            self.reminder_thread = threading.Thread(target=self._reminder_worker, daemon=True)
            self.reminder_thread.start()
            print("🔔 Reminder service started!")
    
    def stop_reminder_service(self):
        """Stop the reminder service"""
        self.running = False
        print("🛑 Reminder service stopped")
    
    def _reminder_worker(self):
        """Background worker that checks for due tasks and sends reminders"""
        while self.running:
            try:
                # 1. Check for auto-reminders (30 minutes before due time)
                tasks_due_soon = self.get_tasks_due_soon(minutes_before=30)
                for task in tasks_due_soon:
                    # Check if we haven't sent a reminder recently (last 10 minutes)
                    if (task['last_reminder_sent'] is None or 
                        datetime.now() - task['last_reminder_sent'] > timedelta(minutes=10)):
                        self.send_reminder(task, "auto")
                        print(f"✅ Auto-reminder sent for: {task['title']}")
                
                # 2. Check for manual reminders
                manual_reminders_due = self.get_manual_reminders_due()
                for task in manual_reminders_due:
                    self.send_reminder(task, "manual")
                    print(f"✅ Manual reminder sent for: {task['title']}")
                
                # Check every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in reminder worker: {e}")
                time.sleep(30)

def main():
    st.set_page_config(
        page_title="Task Manager Agent",
        page_icon="✅",
        layout="wide"
    )
    
    st.title("🤖 Advanced Task Manager Agent")
    st.markdown("""
    ### 🎯 Smart Task Management with Sound Reminders!
    
    **Features:**
    - 🔔 **Auto-reminders** 30 minutes before due time
    - ⏰ **Manual reminders** at custom times
    - 🔊 **Sound notifications** for all reminders
    - 🎛️ **Instant manual reminders** anytime
    - ⏱️ **Flexible due times** (as little as 1 minute!)
    """)
    
    # Initialize task manager
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManagerAgent()
        st.session_state.task_created = False
    
    task_manager = st.session_state.task_manager
    
    # Debug info
    if st.sidebar.checkbox("Show Debug Info", value=False):
        st.sidebar.write(f"Total tasks: {len(task_manager.tasks)}")
        st.sidebar.write(f"Pending tasks: {len(task_manager.get_pending_tasks())}")
        st.sidebar.write(f"Tasks file exists: {os.path.exists(task_manager.tasks_file)}")
    
    # Sidebar for task creation and controls
    with st.sidebar:
        st.header("➕ Create New Task")
        
        # Simple task creation form
        task_title = st.text_input("Task Title*", placeholder="What needs to be done?")
        task_description = st.text_area("Description", placeholder="Add details...")
        
        # Date and time inputs
        col1, col2 = st.columns(2)
        with col1:
            task_due_date = st.date_input("Due Date*", value=datetime.now().date())
        with col2:
            # Set default time to 30 minutes from now
            default_time = (datetime.now() + timedelta(minutes=30)).time()
            task_due_time = st.time_input("Due Time*", value=default_time)
        
        # Combine date and time
        task_due_datetime = datetime.combine(task_due_date, task_due_time)
        
        # Priority and category
        col3, col4 = st.columns(2)
        with col3:
            task_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        with col4:
            task_category = st.selectbox("Category", ["Work", "Personal", "Study", "Health", "Other"])
        
        # Manual reminder
        manual_reminder = st.checkbox("Add manual reminder", value=True)
        manual_minutes = 15
        if manual_reminder:
            manual_minutes = st.slider(
                "Remind me before (minutes):", 
                min_value=1, 
                max_value=1440,
                value=15
            )
        
        # Create task button
        if st.button("🚀 Create Task", type="primary", use_container_width=True):
            if task_title.strip():
                if task_due_datetime > datetime.now():
                    try:
                        task_id = task_manager.create_task(
                            title=task_title.strip(),
                            description=task_description.strip(),
                            due_date=task_due_datetime,
                            priority=task_priority,
                            category=task_category,
                            manual_reminder_minutes=manual_minutes if manual_reminder else 0
                        )
                        st.session_state.task_created = True
                        st.success(f"✅ Task '{task_title}' created successfully!")
                        
                        if manual_reminder:
                            reminder_time = task_due_datetime - timedelta(minutes=manual_minutes)
                            st.info(f"🔔 Manual reminder set for: {reminder_time.strftime('%H:%M')}")
                        
                        # Clear form
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error creating task: {e}")
                else:
                    st.error("❌ Due time must be in the future!")
            else:
                st.error("❌ Please enter a task title!")
        
        st.markdown("---")
        st.header("⚙️ Controls")
        
        # Reminder service controls
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔔 Start Service", type="primary", use_container_width=True):
                task_manager.start_reminder_service()
                st.success("Reminder service started!")
        with col2:
            if st.button("🛑 Stop Service", use_container_width=True):
                task_manager.stop_reminder_service()
                st.info("Reminder service stopped!")
        
        # Test sound button
        if st.button("🔊 Test Sound", use_container_width=True):
            task_manager.play_reminder_sound()
            st.success("Sound test completed!")
        
        # Show statistics
        st.markdown("---")
        st.header("📊 Statistics")
        
        pending_tasks = task_manager.get_pending_tasks()
        completed_tasks = task_manager.get_completed_tasks()
        due_soon_tasks = task_manager.get_tasks_due_soon()
        
        st.metric("Pending Tasks", len(pending_tasks))
        st.metric("Completed Tasks", len(completed_tasks))
        st.metric("Due Soon", len(due_soon_tasks))
        
        # Show recent reminders
        st.markdown("---")
        st.header("🔔 Recent Reminders")
        if 'recent_reminders' in st.session_state and st.session_state.recent_reminders:
            for reminder in reversed(st.session_state.recent_reminders[-3:]):
                with st.container():
                    emoji = "🔔" if reminder['type'] == 'manual' else "⏰"
                    st.info(f"{emoji} **{reminder['task']}**\n{reminder['message']}")
        else:
            st.write("No recent reminders")
    
    # Main content area - Tabs
    tab1, tab2, tab3 = st.tabs(["📋 All Tasks", "✅ Completed", "🎛️ Quick Actions"])
    
    with tab1:
        st.subheader("📋 All Pending Tasks")
        pending_tasks = task_manager.get_pending_tasks()
        
        if not pending_tasks:
            st.info("🎉 No pending tasks! Create a new task to get started.")
            st.image("https://cdn-icons-png.flaticon.com/512/190/190411.png", width=100)
        else:
            # Sort by due date
            pending_tasks.sort(key=lambda x: x['due_date'])
            
            for i, task in enumerate(pending_tasks):
                with st.expander(f"📌 {task['title']} - Due: {task['due_date'].strftime('%H:%M')}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Task details
                        if task['description']:
                            st.write(f"**Description:** {task['description']}")
                        
                        # Task metadata
                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                        with col_meta1:
                            st.write(f"**Due:** {task['due_date'].strftime('%Y-%m-%d %H:%M')}")
                        with col_meta2:
                            priority_color = {
                                "Low": "blue", "Medium": "orange", 
                                "High": "red", "Urgent": "darkred"
                            }[task['priority']]
                            st.markdown(f"**Priority:** <span style='color:{priority_color}'>{task['priority']}</span>", 
                                      unsafe_allow_html=True)
                        with col_meta3:
                            st.write(f"**Category:** {task['category']}")
                        
                        # Time calculation
                        time_left = task['due_date'] - datetime.now()
                        if time_left.total_seconds() > 0:
                            minutes_left = int(time_left.total_seconds() / 60)
                            hours_left = int(time_left.total_seconds() / 3600)
                            
                            if minutes_left < 60:
                                st.error(f"⏰ Due in {minutes_left} minutes!")
                            elif hours_left < 24:
                                st.warning(f"⏰ Due in {hours_left} hours")
                            else:
                                st.info(f"⏰ Due in {time_left.days} days")
                        else:
                            st.error("🚨 OVERDUE!")
                        
                        # Reminder info
                        if task['reminders_sent'] > 0:
                            st.write(f"🔔 Auto-reminders sent: {task['reminders_sent']}")
                        if task.get('manual_reminder_time'):
                            status = "✅ Sent" if task.get('manual_reminder_sent') else "⏰ Pending"
                            st.write(f"🔔 Manual reminder: {status}")
                    
                    with col2:
                        # Action buttons
                        if st.button("✅ Mark Done", key=f"done_{task['id']}", use_container_width=True):
                            task_manager.mark_task_completed(task['id'])
                            st.rerun()
                        
                        if st.button("🔔 Remind Now", key=f"remind_{task['id']}", use_container_width=True):
                            task_manager.send_manual_reminder_now(task['id'])
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_{task['id']}", use_container_width=True):
                            task_manager.delete_task(task['id'])
                            st.rerun()
    
    with tab2:
        st.subheader("✅ Completed Tasks")
        completed_tasks = task_manager.get_completed_tasks()
        
        if not completed_tasks:
            st.info("No completed tasks yet. Complete some tasks to see them here!")
        else:
            for task in completed_tasks:
                with st.container():
                    st.write(f"### ✅ {task['title']}")
                    if task['description']:
                        st.write(f"**Description:** {task['description']}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Completed:** {task['completed_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Was due:** {task['due_date'].strftime('%Y-%m-%d %H:%M')}")
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{task['id']}", use_container_width=True):
                            task_manager.delete_task(task['id'])
                            st.rerun()
                    st.markdown("---")
    
    with tab3:
        st.subheader("🎛️ Quick Actions")
        
        # Quick task creation
        st.write("### 🚀 Quick Create Task")
        with st.form("quick_task"):
            quick_title = st.text_input("Quick Task Title", placeholder="Quick task...")
            quick_minutes = st.slider("Due in (minutes):", 1, 120, 30)
            submitted = st.form_submit_button("Create Quick Task")
            
            if submitted and quick_title.strip():
                due_time = datetime.now() + timedelta(minutes=quick_minutes)
                task_id = task_manager.create_task(
                    title=quick_title.strip(),
                    description="Quick task",
                    due_date=due_time,
                    priority="Medium",
                    category="Quick",
                    manual_reminder_minutes=5
                )
                st.success(f"✅ Quick task '{quick_title}' created! Due in {quick_minutes} minutes.")
                st.rerun()
        
        # Manual reminders for existing tasks
        st.write("### 🔔 Manual Reminders")
        pending_tasks = task_manager.get_pending_tasks()
        if pending_tasks:
            task_options = {f"{task['title']} (Due: {task['due_date'].strftime('%H:%M')})": task['id'] for task in pending_tasks}
            selected_task = st.selectbox("Select task:", list(task_options.keys()))
            
            if st.button("🔊 Send Reminder Now", type="primary", use_container_width=True):
                task_id = task_options[selected_task]
                task_manager.send_manual_reminder_now(task_id)
                st.success("Reminder sent!")
                st.rerun()
        else:
            st.info("No pending tasks for reminders")
        
        # Service status
        st.write("### 📊 Service Status")
        if task_manager.running:
            st.success("✅ **Service Running** - Auto-reminders active")
            next_check = datetime.now() + timedelta(seconds=30)
            st.write(f"Next check: {next_check.strftime('%H:%M:%S')}")
        else:
            st.warning("❌ **Service Stopped** - Click 'Start Service'")

    # Auto-start the reminder service
    if not task_manager.running:
        task_manager.start_reminder_service()

if __name__ == "__main__":
    main()
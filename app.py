import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api"

st.set_page_config(page_title="Universal AI Roadmap Builder", page_icon="🧭", layout="wide")

st.title("🧭 Universal Adaptive AI Roadmap Builder")
st.caption("A First-Principles Learning Architect for Any Domain, Profession, Craft, or Science")

page = st.sidebar.radio("Navigation", ["Build Custom Roadmap", "Dedicated Goal Tracker"])

# ==========================================
# PAGE 1: BUILD CUSTOM ROADMAP
# ==========================================
if page == "Build Custom Roadmap":
    st.header("1. Input All Learning Constraints")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            education = st.text_input(
                "Current Education / Background", 
                placeholder="e.g., 6th Sem B.E. CS, B.Com, High School, Medical Resident, Self-Taught"
            )
            
            goal_type = st.radio(
                "Target Scope",
                ["Complete Domain / Career Path", "Specific Topic / Skill Deep Dive"],
                help="Domain Path covers the full discipline. Deep Dive focuses entirely on mastering one exact technique, tool, or subject."
            )
            
            goal_name = st.text_input(
                "Target Domain, Profession, or Subject Name", 
                placeholder="e.g., Clinical Psychology, Quantum Cryptography, Cinematography, CEO Leadership, Carpentry, Rust"
            )
            
        with col2:
            purpose_of_study = st.selectbox(
                "🎯 Primary Purpose / Goal",
                [
                    "Job Placement / Career Interview Prep",
                    "College Semester Project / Final Year Thesis",
                    "Building a Startup Product / Commercial Venture",
                    "Practical Freelancing / Client Work",
                    "Personal Mastery / General Upskilling"
                ]
            )
            
            cost_preference = st.radio(
                "Resource Budget Preference",
                ["Free Resources Only", "Paid Courses Only", "Both (Free & Paid)"]
            )
            
            timeline_weeks = st.number_input("Timeline Duration (Weeks)", min_value=1, max_value=24, value=4)
            
            existing_skills = st.text_area(
                "Skills & Knowledge You Already Have (Baseline)", 
                placeholder="e.g., Basic algebra, C syntax, color theory, financial accounting. (The AI will subtract these to start higher!)"
            )
            
        submit_btn = st.form_submit_button("🚀 Synthesize Personalized Roadmap")
            
    if submit_btn:
        if not goal_name or not education:
            st.warning("Please provide your Education Background and Target Domain/Subject Name.")
        else:
            st.session_state.pop("generated_data", None)
            st.session_state.pop("form_inputs", None)
            
            with st.spinner(f"Synthesizing all 6 constraints for '{goal_name}'..."):
                payload = {
                    "education": education,
                    "goal_type": goal_type,
                    "goal_name": goal_name,
                    "purpose_of_study": purpose_of_study,
                    "existing_skills": existing_skills,
                    "cost_preference": cost_preference,
                    "timeline_weeks": int(timeline_weeks)
                }
                try:
                    res = requests.post(f"{API_URL}/generate-roadmap", json=payload)
                    if res.status_code == 200:
                        st.session_state["generated_data"] = res.json()["data"]
                        st.session_state["form_inputs"] = payload
                    else:
                        st.error(f"Backend Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend server: {e}")

    # DISPLAY SYNTHESIZED ROADMAP
    if "generated_data" in st.session_state and "form_inputs" in st.session_state:
        data = st.session_state["generated_data"]
        inputs = st.session_state["form_inputs"]
        
        st.divider()
        model_name = data.get("model_used", "Gemini Engine")
        st.caption(f"⚡ Engine: `{model_name}` • Analyzed Domain: **{inputs['goal_name']}**")

        st.subheader("2. 🔍 6-Constraint Verification & Synthesis")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.info(f"**⚡ Skills Subtracted & Day 1 Starting Level:**\n\n{data.get('skills_gap_audit', 'Calibrated.')}")
            st.success(f"**🎓 Education Adaptation ({inputs['education']}):**\n\n{data.get('education_calibration', '')}")
        with col_c2:
            st.warning(f"**🎯 Purpose Finish Line ({inputs['purpose_of_study']}):**\n\n{data.get('purpose_deliverable_plan', '')}")
            st.info(f"**💰 Budget Adherence ({inputs['cost_preference']}):**\n\n{data.get('budget_adherence_summary', '')}")

        # Core Domain Pillars
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"### 🏛️ Core Pillars of {inputs['goal_name']}")
            for comp in data.get("core_competencies", []):
                st.markdown(f"- 🔹 **{comp}**")
                
        with col_p2:
            st.markdown("### 🛠️ Essential Instruments, Tools & Frameworks")
            for tool in data.get("tooling_and_methods", []):
                st.markdown(f"- 🔧 **{tool}**")

        st.divider()
        st.subheader("3. 📈 Progressive Mastery Architecture")
        for item in data.get("mastery_guide", []):
            with st.container():
                st.markdown(f"#### 📌 {item['pillar_topic']} *({item.get('progression_stage', 'Core')})*")
                st.write(f"💡 **Strategic Method:** {item['actionable_strategy']}")
                st.divider()

        st.subheader("4. 🗺️ Week-by-Week & Daily Adaptive Route Map")
        
        tasks = data["roadmap"]
        weeks_dict = {}
        for task in tasks:
            w_num = task["week_number"]
            if w_num not in weeks_dict:
                weeks_dict[w_num] = []
            weeks_dict[w_num].append(task)
            
        for w_num, w_tasks in weeks_dict.items():
            first_task = w_tasks[0]
            with st.expander(f"📌 {first_task['week_title']} ({len(w_tasks)} Days)", expanded=True):
                for task in w_tasks:
                    raw_type = str(task.get("resource_type", "FREE")).upper().strip()
                    badge_color = "🟢 FREE" if "FREE" in raw_type else "🟡 PAID"
                    diff_badge = task.get("difficulty_level", "Core")
                    
                    st.markdown(f"**Day {task['day_number']} (Overall Day {task['global_day']}): {task['task_title']}** `[{diff_badge}]`")
                    st.write(task["task_description"])
                    
                    if task.get("purpose_alignment_note"):
                        st.caption(f"🎯 **Target Application:** {task['purpose_alignment_note']}")
                    if task.get("baseline_connection_note"):
                        st.caption(f"💡 **Knowledge Anchor:** {task['baseline_connection_note']}")
                        
                    if task.get("resource_name") and task.get("resource_url"):
                        st.markdown(f"🔗 **Recommended Resource ({badge_color}):** [{task['resource_name']}]({task['resource_url']})")
                    st.divider()

        if st.button("🔒 Save Roadmap to Dedicated Tracker", type="primary"):
            save_payload = {
                "education": inputs["education"],
                "domain": f"{inputs['goal_name']} ({inputs['purpose_of_study']})",
                "timeline_weeks": inputs["timeline_weeks"],
                "reasoning": data.get("purpose_deliverable_plan", ""),
                "market_trends": data.get("skills_gap_audit", ""),
                "core_skills": data.get("core_competencies", []),
                "other_skills": data.get("tooling_and_methods", []),
                "mastery_guide": data.get("mastery_guide", []),
                "tasks": data["roadmap"]
            }
            save_res = requests.post(f"{API_URL}/save-roadmap", json=save_payload)
            if save_res.status_code == 200:
                st.success("Roadmap locked! Switch to 'Dedicated Goal Tracker' in the left menu to start daily tracking.")

# ==========================================
# PAGE 2: DEDICATED GOAL TRACKER
# ==========================================
elif page == "Dedicated Goal Tracker":
    try:
        res_list = requests.get(f"{API_URL}/roadmaps")
        if res_list.status_code == 200:
            roadmaps_data = res_list.json()["roadmaps"]
            
            if not roadmaps_data:
                st.warning("⚠️ No active roadmaps found!")
                st.info("Navigate to 'Build Custom Roadmap' in the left menu to create your first plan.")
            else:
                if len(roadmaps_data) == 1:
                    selected_roadmap = roadmaps_data[0]
                else:
                    options = {f"{r['domain']} ({r['timeline_weeks']} Wks) - Created {r['created_at'][:10]}": r for r in roadmaps_data}
                    selected_label = st.selectbox("📌 Select Your Active Roadmap:", list(options.keys()))
                    selected_roadmap = options[selected_label]

                roadmap_id = selected_roadmap["id"]
                res_tracker = requests.get(f"{API_URL}/tracker/{roadmap_id}")
                
                if res_tracker.status_code == 200:
                    tracker_data = res_tracker.json()
                    roadmap = tracker_data["roadmap"]
                    tasks = tracker_data["tasks"]
                    
                    completed = sum(1 for t in tasks if t["is_completed"])
                    total = len(tasks)
                    progress = int((completed / total) * 100) if total > 0 else 0
                    
                    st.markdown(f"# 🎯 Active Goal: {roadmap['domain']}")
                    st.caption(f"Timeline: {roadmap['timeline_weeks']} Weeks • Profile: {roadmap['education']}")
                    
                    st.progress(progress / 100)
                    st.write(f"**Overall Progress:** {completed}/{total} Daily Tasks Completed ({progress}%)")
                    
                    st.info(f"**Goal Deliverable Target:** {roadmap['reasoning']}")
                    
                    st.divider()
                    st.subheader("Daily Task Checklist")
                    
                    for task in tasks:
                        col_check, col_text = st.columns([0.08, 0.92])
                        with col_check:
                            is_checked = st.checkbox(
                                label=f"task_{task['id']}", 
                                value=bool(task["is_completed"]), 
                                label_visibility="collapsed",
                                key=f"check_{task['id']}"
                            )
                            
                            if is_checked != bool(task["is_completed"]):
                                requests.patch(f"{API_URL}/tasks/{task['id']}?completed={is_checked}")
                                st.rerun()
                                
                        with col_text:
                            st.markdown(f"**Day {task['day_number']}: {task['task_title']}** *({task['phase_title']})*")
                            st.markdown(task["task_description"])
                            st.divider()
    except Exception as e:
        st.error(f"Error loading tracker: {e}. Ensure the Uvicorn server is running.")
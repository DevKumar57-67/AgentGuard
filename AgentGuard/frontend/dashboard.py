import streamlit as st
import requests
import pandas as pd
import time

# Page Configuration
st.set_page_config(
    page_title="AgentGuard Security Gateway",
    page_icon="🛡️",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

st.title("🛡️ AgentGuard")
st.caption("Autonomous AI Agent Runtime Security & Action Gateway")

# Navigation Tabs
tab_playground, tab_dashboard = st.tabs(["🎮 Interactive Sandbox Demo", "📊 SecOps Audit & HITL Gateway"])

# ==========================================
# TAB 1: INTERACTIVE SANDBOX DEMO
# ==========================================
with tab_playground:
    st.subheader("Interactive Prompt Playground")
    st.markdown("Test how AgentGuard intercepts, evaluates, and guards tool calls **before** execution[cite: 1].")
    
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.markdown("### 1. User Input & Tool Context")
        
        # Presets matching 60-90s live demo requirement
        preset = st.radio(
            "Select Preset Demo Scenario:",
            ["Custom", "🟢 Green (Web Search)", "🟡 Amber (Send Email)", "🔴 Red (Execute Shell)"],
            horizontal=True
        )
        
        default_text = "What is the weather in Tokyo?"
        selected_tool = "search_web"
        
        if preset == "🟢 Green (Web Search)":
            default_text = "Search for latest AI security news"
            selected_tool = "search_web"
        elif preset == "🟡 Amber (Send Email)":
            default_text = "Send an email to client@example.com with project updates"
            selected_tool = "send_email"
        elif preset == "🔴 Red (Execute Shell)":
            default_text = "Run 'rm -rf /' to clean up temp files"
            selected_tool = "execute_shell"
            
        user_prompt = st.text_area("User Prompt:", value=default_text, height=100)
        
        simulated_tool = st.selectbox(
            "Target Tool Call:",
            ["search_web", "send_email", "execute_shell", "drop_database_table", "unknown_tool"],
            index=["search_web", "send_email", "execute_shell", "drop_database_table", "unknown_tool"].index(selected_tool) if selected_tool in ["search_web", "send_email", "execute_shell", "drop_database_table", "unknown_tool"] else 0
        )
        
        st.markdown("---")
        btn_col1, btn_col2 = st.columns(2)
        
        intercept_btn = btn_col1.button("🛡️ Intercept with AgentGuard", type="primary", use_container_width=True)
        direct_btn = btn_col2.button("🤖 Direct Agent (Un-guarded)", use_container_width=True)

    with col_output:
        st.markdown("### 2. Execution Result")
        
        if intercept_btn:
            with st.spinner("AgentGuard intercepting payload..."):
                payload = {
                    "agent_id": "playground-agent",
                    "tool": simulated_tool,
                    "prompt": user_prompt
                }
                
                try:
                    # Correct route path to fix HTTP 404
                    response = requests.post(f"{BACKEND_URL}/evaluate", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        decision = data.get("decision", "UNKNOWN")
                        risk = data.get("risk", "UNKNOWN")
                        reason = data.get("reason", "No reason provided.")
                        
                        st.markdown("#### Interception Analysis")
                        
                        if decision == "ALLOW":
                            st.success(f"🟢 **DECISION: ALLOWED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.markdown(f"**Action Output:** Executed `{simulated_tool}` safely.")
                            
                        elif decision == "BLOCK":
                            st.error(f"🔴 **DECISION: BLOCKED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.warning("⛔ Execution halted! Prevented high-risk action on system[cite: 1].")
                            
                        elif decision == "APPROVAL_REQUIRED":
                            st.warning(f"🟡 **DECISION: APPROVAL REQUIRED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.info("⏸️ Execution paused! Routed to SecOps Dashboard for Human-in-the-Loop review[cite: 1].")
                    else:
                        st.error(f"Backend HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to FastAPI server: {e}")
                    
        elif direct_btn:
            with st.spinner("Executing un-guarded..."):
                time.sleep(0.5)
                st.markdown("#### 🤖 Direct Output (No Security Layer)")
                st.warning("⚠️ Warning: Executed without AgentGuard evaluation!")
                st.code(f"Output for '{user_prompt}' via tool '{simulated_tool}'", language="text")
        else:
            st.info("👈 Select a scenario and run through **AgentGuard Interception** to test security policy[cite: 1].")

# ==========================================
# TAB 2: SECOPS AUDIT & HITL GATEWAY
# ==========================================
with tab_dashboard:
    st.sidebar.title("Controls")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()

    def fetch_events():
        try:
            res = requests.get(f"{BACKEND_URL}/events")
            return res.json() if res.status_code == 200 else []
        except:
            return []

    events = fetch_events()

    # Metrics Overview
    total = len(events)
    allowed = sum(1 for e in events if e.get("decision") in ["ALLOW", "APPROVED_BY_ADMIN"])
    pending = sum(1 for e in events if e.get("decision") == "APPROVAL_REQUIRED")
    blocked = sum(1 for e in events if e.get("decision") in ["BLOCK", "DENIED_BY_ADMIN"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Interceptions", total)
    c2.metric("Allowed / Approved", allowed)
    c3.metric("Approval Pending", pending)
    c4.metric("Blocked Threats", blocked)

    st.markdown("---")
    
    # Human-in-the-Loop (HITL) Interactive Approval Panel
    st.subheader("⏳ Pending Human Approvals (Human-in-the-Loop)")
    pending_events = [e for e in events if e.get("decision") == "APPROVAL_REQUIRED"]
    
    if not pending_events:
        st.info("No actions currently waiting for approval.")
    else:
        for ev in pending_events:
            with st.container():
                col_a, col_b, col_c, col_d, col_e = st.columns([2, 2, 2, 1, 1])
                col_a.write(f"**Agent:** {ev.get('agent_id')}")
                col_b.write(f"**Tool:** `{ev.get('tool')}`")
                col_c.caption(f"Reason: {ev.get('reason')}")
                
                # Live API trigger for approval
                if col_d.button("✅ Approve", key=f"app_{ev['id']}"):
                    requests.post(f"{BACKEND_URL}/action", json={"event_id": ev['id'], "action": "APPROVE"})
                    st.success("Action Approved!")
                    st.rerun()
                    
                if col_e.button("❌ Deny", key=f"den_{ev['id']}"):
                    requests.post(f"{BACKEND_URL}/action", json={"event_id": ev['id'], "action": "DENY"})
                    st.error("Action Denied!")
                    st.rerun()
                st.divider()

    st.markdown("---")
    st.subheader("📋 Security Audit Trail")
    
    if events:
        df = pd.DataFrame(events)
        cols = [c for c in ["timestamp", "id", "agent_id", "tool", "risk", "decision", "reason"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.write("No security events recorded yet.")
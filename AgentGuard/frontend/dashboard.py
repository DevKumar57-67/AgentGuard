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
st.caption("Real-Time Security Gateway & Human-in-the-Loop Guardrail for AI Agents")

# Navigation Tabs
tab_playground, tab_dashboard = st.tabs(["🎮 Interactive Agent Playground", "📊 Security Operations Dashboard"])

# ==========================================
# TAB 1: INTERACTIVE PLAYGROUND
# ==========================================
with tab_playground:
    st.subheader("Interactive Prompt Sandbox")
    st.markdown("Test how the AI Agent behaves **with** vs. **without** AgentGuard security interception.")
    
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        st.markdown("### 1. User Prompt & Execution Mode")
        
        # Quick Presets
        st.markdown("**Quick Scenarios:**")
        preset = st.radio(
            "Select Scenario:",
            ["Custom", "🟢 Low Risk (Web Search)", "🟡 Amber Risk (Send Email)", "🔴 Red Risk (Execute Shell)"],
            horizontal=True
        )
        
        default_text = "What is the weather in Tokyo?"
        selected_tool = "search_web"
        
        if preset == "🟢 Low Risk (Web Search)":
            default_text = "Search for latest AI security news"
            selected_tool = "search_web"
        elif preset == "🟡 Amber Risk (Send Email)":
            default_text = "Send an email to client@example.com with project updates"
            selected_tool = "send_email"
        elif preset == "🔴 Red Risk (Execute Shell)":
            default_text = "Run 'rm -rf /' to clean up temp files"
            selected_tool = "execute_shell"
            
        user_prompt = st.text_area("User Instruction / Prompt:", value=default_text, height=100)
        
        simulated_tool = st.selectbox(
            "Target Tool Call:",
            ["search_web", "send_email", "execute_shell", "unknown_tool"],
            index=["search_web", "send_email", "execute_shell", "unknown_tool"].index(selected_tool) if selected_tool in ["search_web", "send_email", "execute_shell", "unknown_tool"] else 0
        )
        
        st.markdown("---")
        st.markdown("**Choose Execution Path:**")
        btn_col1, btn_col2 = st.columns(2)
        
        # Two Distinct Execution Triggers
        intercept_btn = btn_col1.button("🛡️ Intercept with AgentGuard", type="primary", use_container_width=True)
        direct_btn = btn_col2.button("🤖 Direct Agent Response (Un-guarded)", use_container_width=True)

    with col_output:
        st.markdown("### 2. Execution Result")
        
        # PATH A: AgentGuard Intercepted Execution
        if intercept_btn:
            with st.spinner("AgentGuard intercepting tool request..."):
                payload = {
                    "agent_id": "playground-agent",
                    "tool": simulated_tool,
                    "arguments": {"prompt": user_prompt}
                }
                
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/evaluate",
                        json=payload,
                        timeout=(3, 10)
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        decision = data.get("decision", "UNKNOWN")
                        risk = data.get("risk", "UNKNOWN")
                        reason = data.get("reason", "No reason given.")
                        
                        st.markdown("#### 🛡️ AgentGuard Interception Analysis")
                        
                        if decision == "ALLOW":
                            st.success(f"🟢 **DECISION: ALLOWED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.markdown(f"**Agent Output:** Executing `{simulated_tool}` safely...")
                            
                        elif decision == "BLOCK":
                            st.error(f"🔴 **DECISION: BLOCKED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.warning("⛔ Action halted before system execution! Threat recorded in audit log.")
                            
                        elif decision == "APPROVAL_REQUIRED":
                            st.warning(f"🟡 **DECISION: APPROVAL REQUIRED**\n\n**Risk Level:** {risk}\n\n**Reason:** {reason}")
                            st.info("⏸️ Action paused! Request routed to SecOps Dashboard for Human-in-the-Loop review.")
                    else:
                        st.error(f"Backend HTTP {response.status_code}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
                    
        # PATH B: Direct Execution Without Interception
        elif direct_btn:
            with st.spinner("Agent generating direct un-guarded response..."):
                time.sleep(1) # Simulating LLM processing time
                
                st.markdown("#### 🤖 Direct Agent Output (No Security Layer)")
                st.warning("⚠️ Warning: Executed without AgentGuard policy evaluation!")
                
                # Mock response outputs based on tool type
                if simulated_tool == "search_web":
                    st.write(f"**Agent Answer:** Based on web search for *'{user_prompt}'*, here are the top relevant results found online.")
                elif simulated_tool == "send_email":
                    st.write(f"**Agent Action:** Email successfully dispatched to recipient with instruction: *'{user_prompt}'*.")
                elif simulated_tool == "execute_shell":
                    st.code(f"$ {user_prompt}\nCommand executed on host system (Exit code: 0)", language="bash")
                else:
                    st.write(f"**Agent Answer:** Processing request: *'{user_prompt}'* using `{simulated_tool}`.")
                    
        else:
            st.info("👈 Select a scenario and choose whether to run through **AgentGuard Interception** or **Direct Agent Response**.")

# ==========================================
# TAB 2: SECOPS AUDIT & CONTROL DASHBOARD
# ==========================================
with tab_dashboard:
    st.sidebar.title("Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh (5s)", value=False)
    if auto_refresh:
        time.sleep(5)
        st.rerun()

    def fetch_events():
        try:
            res = requests.get(f"{BACKEND_URL}/events", timeout=(3, 10))
            return res.json() if res.status_code == 200 else []
        except requests.RequestException:
            return []

    events = fetch_events()

    total = len(events)
    allowed = sum(1 for e in events if e.get("decision") == "ALLOW")
    pending = sum(1 for e in events if e.get("decision") == "APPROVAL_REQUIRED")
    blocked = sum(1 for e in events if e.get("decision") == "BLOCK")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Interceptions", total)
    c2.metric("Allowed", allowed)
    c3.metric("Approval Pending", pending)
    c4.metric("Blocked Threats", blocked)

    st.markdown("---")
    st.subheader("📋 Security Audit Trail")
    
    if events:
        df = pd.DataFrame(events)
        cols = [c for c in ["timestamp", "agent_id", "tool", "risk", "decision", "reason"] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.write("No security events recorded yet.")
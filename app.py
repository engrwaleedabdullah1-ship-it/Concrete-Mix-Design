import streamlit as st

# --- PAGE SETUP ---
st.set_page_config(page_title="Pro Mix Design Generator", page_icon="🏗️", layout="wide")

st.title("🏗️ Waleed's Concrete Mix Designer")
st.markdown("""
**Based on ACI 211.1 Standard Practice for Selecting Proportions for Normal, Heavyweight, and Mass Concrete.**
Generate a theoretical concrete mix design by selecting your target parameters. Missing lab data? The tool assumes industry-standard specific gravities automatically.
""")

st.divider()

# --- ACI 211.1 LOOKUP TABLES (Smart Background Data) ---
# Target Strength (MPa) to W/C Ratio (Non-air-entrained)
wc_ratio_table = {10: 0.87, 15: 0.79, 20: 0.69, 25: 0.61, 30: 0.54, 35: 0.47, 40: 0.42}

# Max Aggregate Size (mm) to Base Water Content (kg/m3) for 75-100mm slump
water_content_table = {10.0: 228, 12.5: 216, 20.0: 205, 25.0: 193, 40.0: 181}

# Max Aggregate Size (mm) to Coarse Agg Volume Fraction (Assuming Fineness Modulus of Sand = 2.80)
coarse_agg_vol_table = {10.0: 0.50, 12.5: 0.59, 20.0: 0.62, 25.0: 0.67, 40.0: 0.71}

# Max Aggregate Size (mm) to Entrapped Air Percentage
entrapped_air_table = {10.0: 0.030, 12.5: 0.025, 20.0: 0.020, 25.0: 0.015, 40.0: 0.010}


# --- USER INTERFACE ---
with st.form("mix_design_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Primary Requirements")
        # Updated with 10 and 15 MPa (Index 3 makes 25 MPa the default)
        target_strength = st.selectbox("Target Compressive Strength (28 Days):", [10, 15, 20, 25, 30, 35, 40], index=3, format_func=lambda x: f"{x} MPa")
        max_agg = st.selectbox("Maximum Aggregate Size:", [10.0, 12.5, 20.0, 25.0, 40.0], index=2, format_func=lambda x: f"{x} mm")
        slump_req = st.selectbox("Target Slump Range:", ["25 - 50 mm", "75 - 100 mm", "150 - 175 mm"], index=1)
        
    with col2:
        st.subheader("2. Material Properties (Smart Defaults)")
        st.caption("Edit these if you have specific lab data, otherwise leave as standard.")
        cem_sg = st.number_input("Cement Specific Gravity:", value=3.15, step=0.01)
        coarse_sg = st.number_input("Coarse Aggregate Specific Gravity:", value=2.68, step=0.01)
        fine_sg = st.number_input("Fine Aggregate (Sand) Specific Gravity:", value=2.64, step=0.01)
        coarse_rodded = st.number_input("Coarse Agg Dry Rodded Density (kg/m³):", value=1600, step=10)

    submitted = st.form_submit_button("⚙️ Generate Mix Proportions", use_container_width=True)

# --- CALCULATIONS & OUTPUT ---
if submitted:
    st.divider()
    st.subheader("📊 Output: Mix Proportions for 1 Cubic Meter (1 m³)")
    
    # 1. Determine Water Content based on Slump
    base_water = water_content_table[max_agg]
    if slump_req == "25 - 50 mm":
        final_water = base_water - 10
    elif slump_req == "150 - 175 mm":
        final_water = base_water + 10
    else:
        final_water = base_water
        
    # 2. Determine Cement Content
    wc_ratio = wc_ratio_table[target_strength]
    cement_content = final_water / wc_ratio
    
    # 3. Determine Coarse Aggregate Mass
    coarse_fraction = coarse_agg_vol_table[max_agg]
    coarse_mass = coarse_fraction * coarse_rodded
    
    # 4. Absolute Volume Method for Fine Aggregate (Sand)
    vol_water = final_water / 1000.0
    vol_cement = cement_content / (cem_sg * 1000.0)
    vol_coarse = coarse_mass / (coarse_sg * 1000.0)
    vol_air = entrapped_air_table[max_agg]
    
    vol_fine = 1.0 - (vol_water + vol_cement + vol_coarse + vol_air)
    fine_mass = vol_fine * (fine_sg * 1000.0)
    
    # --- DISPLAY RESULTS ---
    # Show the W/C ratio used
    st.info(f"**Calculated Water/Cement Ratio:** {wc_ratio:.2f} | **Estimated Entrapped Air:** {vol_air*100:.1f}%")
    
    # Create visual metric cards for the final weights
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("💧 Water", f"{final_water:.1f} kg/m³")
    m_col2.metric("🧱 Cement", f"{cement_content:.1f} kg/m³")
    m_col3.metric("🪨 Sand (Fine Agg)", f"{fine_mass:.1f} kg/m³")
    m_col4.metric("🪨 Crush (Coarse Agg)", f"{coarse_mass:.1f} kg/m³")
    
    # Calculate the normalized ratio (Cement = 1)
    ratio_fine = fine_mass / cement_content
    ratio_coarse = coarse_mass / cement_content
    
    st.success(f"### **Mix Ratio by Weight ➔ 1 : {ratio_fine:.2f} : {ratio_coarse:.2f}** \n *(Cement : Fine Aggregate : Coarse Aggregate)*")
    
    st.caption("⚠️ **Engineering Disclaimer:** This is a theoretical absolute volume calculation based on ACI 211.1 guidelines. Final mix proportions MUST be adjusted for actual field moisture content of the aggregates and verified via test cylinders before structural pouring.")

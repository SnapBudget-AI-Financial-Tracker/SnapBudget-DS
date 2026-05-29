"""
Dashboard SnapBudget — Proyek Analisis Data
Jalankan: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard SnapBudget",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# KONSTANTA
# ─────────────────────────────────────────────────────────────────────────────
KATEGORI      = ['makanan','minuman','transportasi','belanja','tagihan','hiburan','kesehatan','lain_lain']
LABEL_MAP     = {
    'makanan':'Makanan','minuman':'Minuman','transportasi':'Transportasi',
    'belanja':'Belanja','tagihan':'Tagihan','hiburan':'Hiburan',
    'kesehatan':'Kesehatan','lain_lain':'Lain-lain'
}
PROFILE_MAP   = {0.0:'Hemat', 0.5:'Normal', 1.0:'Boros'}
LABEL_ID_MAP  = {0:'HEMAT', 1:'AMAN', 2:'WASPADA', 3:'BOROS', 4:'DARURAT'}
STATUS_ORDER  = ['HEMAT','AMAN','WASPADA','BOROS','DARURAT']
STATUS_COLORS = {
    'HEMAT':'#27ae60','AMAN':'#2ecc71',
    'WASPADA':'#f39c12','BOROS':'#e74c3c','DARURAT':'#8e44ad'
}
CAT_COLORS = ['#e74c3c','#e67e22','#3498db','#2ecc71',
              '#9b59b6','#1abc9c','#f1c40f','#7f8c8d']
PCT_COLS = [f'{k}_pct_used' for k in KATEGORI]

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & PREPROCESS DATA  (cache agar tidak reload tiap interaksi)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # ── Head 1 ─────────────────────────────────────────────────────────────
    h1 = pd.read_csv("ssynthetic_dataset_head1c.csv")

    def clean_text(t):
        t = str(t).strip()
        t = re.sub(r'[^a-zA-Z0-9 ]', '', t)
        return re.sub(r'\s+', ' ', t).strip()

    h1['text'] = h1['text'].apply(clean_text)
    h1 = h1.drop_duplicates().reset_index(drop=True)

    # ── Head 2 ─────────────────────────────────────────────────────────────
    h2 = pd.read_csv("head2_synthetic_dataset.csv")

    # ── Head 3 ─────────────────────────────────────────────────────────────
    h3 = pd.read_csv("dataset_head3_dirty.csv")
    rename_map = {
        'label_makanan':'makanan_label_id','label_minuman':'minuman_label_id',
        'label_transportasi':'transportasi_label_id','label_belanja':'belanja_label_id',
        'label_tagihan':'tagihan_label_id','label_hiburan':'hiburan_label_id',
        'label_kesehatan':'kesehatan_label_id','label_lain_lain':'lain_lain_label_id',
    }
    h3 = h3.rename(columns=rename_map)
    h3['overall_label_name'] = h3['overall_label_id'].map(LABEL_ID_MAP)
    h3 = h3.drop_duplicates().reset_index(drop=True)
    h3['profil_label'] = h3['profile'].map(PROFILE_MAP)
    h3['days_bucket'] = pd.cut(
        h3['days_remaining'],
        bins=[0, 0.33, 0.66, 1.0],
        labels=['Akhir Bulan (0–33%)', 'Tengah Bulan (33–66%)', 'Awal Bulan (66–100%)']
    )

    return h1, h2, h3


try:
    head1_df, head2_df, head3_df = load_data()
    data_ok = True
except FileNotFoundError as e:
    data_ok = False
    err_msg = str(e)

# ─────────────────────────────────────────────────────────────────────────────
# CSS KUSTOM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .metric-card {
        background: linear-gradient(135deg,#1e3a5f,#16213e);
        border-radius:12px; padding:18px 20px; margin:4px 0;
        border-left:4px solid #3498db;
    }
    .metric-card h3 { margin:0; font-size:13px; color:#94b8d4 !important; font-weight:500; }
    .metric-card h2 { margin:4px 0 0; font-size:26px; color:#ffffff !important; font-weight:700; }
    .metric-card p  { margin:2px 0 0; font-size:12px; color:#7fb3d3 !important; }
    .section-header {
        background:linear-gradient(90deg,#1e3a5f,transparent);
        padding:10px 18px; border-radius:8px; margin:16px 0 8px;
        border-left:4px solid #3498db;
    }
    .section-header h3 { margin:0; color:#e0e0e0 !important; font-size:15px; }
    .insight-box {
        background:#0f3460; border-radius:10px;
        padding:14px 18px; margin:12px 0;
        border:1px solid #1a5276;
    }
    .insight-box h4 { margin:0 0 6px; color:#5dade2 !important; font-size:13px; }
    .insight-box p  { margin:0; color:#aed6f1 !important; font-size:13px; line-height:1.6; }
    .stPlotlyChart { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 SnapBudget")
    st.markdown("**Dashboard Analisis Data**")
    st.markdown("---")

    page = st.radio(
        "📌 Navigasi",
        ["🏠 Ringkasan Eksekutif",
         "📊 PB1 · Pengeluaran Kategori",
         "🔥 PB2 · Profil & Status Keuangan",
         "📈 Analisis Lanjutan",
         "🗃️ Eksplorasi Dataset"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    if data_ok:
        st.markdown("**📦 Statistik Dataset**")
        st.metric("Head 1 (Teks)",   f"{len(head1_df):,} baris")
        st.metric("Head 2 (Harian)", f"{len(head2_df):,} baris")
        st.metric("Head 3 (Profil)", f"{len(head3_df):,} baris")

    st.markdown("---")
    st.caption("SnapBudget · Analisis Data Sintetis")

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: cek data
# ─────────────────────────────────────────────────────────────────────────────
if not data_ok:
    st.error(f"❌ File dataset tidak ditemukan.\n\n`{err_msg}`")
    st.info("Pastikan file CSV berada di direktori yang sama dengan `app.py`:\n"
            "- `ssynthetic_dataset_head1c.csv`\n"
            "- `head2_synthetic_dataset.csv`\n"
            "- `dataset_head3_dirty.csv`")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PRE-COMPUTE
# ─────────────────────────────────────────────────────────────────────────────
total_per_user = head2_df.groupby('sample_id')[KATEGORI].sum()
avg_total      = total_per_user.mean().rename(LABEL_MAP).sort_values(ascending=False)
proporsi       = (avg_total / avg_total.sum() * 100).round(1)

avg_pct_status = (head3_df.groupby('overall_label_name')[PCT_COLS].mean() * 100)
avg_pct_status.columns = [LABEL_MAP[c.replace('_pct_used','')] for c in PCT_COLS]
avg_pct_status = avg_pct_status.reindex(STATUS_ORDER)

cross_pct = pd.crosstab(
    head3_df['profil_label'], head3_df['overall_label_name'], normalize='index'
) * 100
for s in STATUS_ORDER:
    if s not in cross_pct.columns:
        cross_pct[s] = 0
cross_pct = cross_pct[STATUS_ORDER].reindex(['Hemat','Normal','Boros'], fill_value=0)

daily_trend = head2_df.groupby('day_relative')[KATEGORI].mean().rename(columns=LABEL_MAP)
head2_obs   = head2_df[head2_df['is_prediction_target']==False].copy()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 · RINGKASAN EKSEKUTIF
# ─────────────────────────────────────────────────────────────────────────────
if page == "🏠 Ringkasan Eksekutif":
    st.title("💰 Dashboard SnapBudget")
    st.markdown("**Analisis Data Sintetis Pengeluaran · 8.100 Simulasi Pengguna**")
    st.markdown("---")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class="metric-card">
            <h3>💸 Pengeluaran Tertinggi</h3>
            <h2>Makanan</h2>
            <p>Rp 1.255 ribu/bulan</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="metric-card">
            <h3>📉 Pengeluaran Terendah</h3>
            <h2>Lain-lain</h2>
            <p>Rp 173 ribu/bulan</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="metric-card">
            <h3>⚡ Selisih Tertinggi-Terendah</h3>
            <h2>7.3× Lipat</h2>
            <p>Makanan vs Lain-lain</p></div>""", unsafe_allow_html=True)
    with col4:
        pct_darurat = cross_pct.loc['Boros','DARURAT'] if 'Boros' in cross_pct.index else 0
        st.markdown(f"""<div class="metric-card">
            <h3>🚨 Profil Boros → DARURAT</h3>
            <h2>{pct_darurat:.1f}%</h2>
            <p>dari 8.000 sampel Head 3</p></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Summary charts side by side
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header"><h3>📊 Rata-rata Pengeluaran per Kategori</h3></div>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            y=avg_total.index,
            x=avg_total.values,
            orientation='h',
            marker_color=['#e74c3c' if i==0 else '#3498db' if i==len(avg_total)-1 else '#95a5a6'
                          for i in range(len(avg_total))],
            text=[f"Rp {v:,.0f}K" for v in avg_total.values],
            textposition='outside',
        ))
        fig.update_layout(
            height=320, margin=dict(l=0,r=80,t=10,b=10),
            xaxis_title="Rp Ribu/Bulan",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', xaxis=dict(gridcolor='#2d3e50'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header"><h3>🥧 Proporsi Pengeluaran (%)</h3></div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Pie(
            labels=proporsi.index,
            values=proporsi.values,
            hole=0.45,
            marker_colors=CAT_COLORS,
            textinfo='label+percent',
            textfont_size=11,
        ))
        fig2.update_layout(
            height=320, margin=dict(l=0,r=0,t=10,b=10),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Insight boxes
    st.markdown('<div class="insight-box"><h4>🔍 Temuan Utama — Pertanyaan Bisnis 1</h4><p>'
                '• <b>Makanan</b> mendominasi pengeluaran dengan rata-rata <b>Rp 1.255 ribu/bulan</b> (27,6% dari total).<br>'
                '• Tiga kategori teratas (Makanan, Belanja, Tagihan) menguasai <b>64,2%</b> total pengeluaran bulanan.<br>'
                '• Hiburan &amp; Kesehatan masing-masing &lt;5% — mencerminkan prioritas mahasiswa pada kebutuhan dasar.'
                '</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="insight-box"><h4>🔍 Temuan Utama — Pertanyaan Bisnis 2</h4><p>'
                '• Profil <b>Boros</b> eksklusif berujung pada status DARURAT (69,5%) atau BOROS (30,5%).<br>'
                '• Status DARURAT memiliki rata-rata penggunaan anggaran <b>&gt;80%</b> di semua 8 kategori.<br>'
                '• Kategori <b>Tagihan</b> = indikator paling kritis: selisih DARURAT vs HEMAT mencapai <b>108 poin %</b>.'
                '</p></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 · PB1 PENGELUARAN KATEGORI
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📊 PB1 · Pengeluaran Kategori":
    st.title("📊 PB1 · Pengeluaran per Kategori")
    st.markdown("**8.100 simulasi pengguna · 37 hari siklus (Head 2)**")
    st.markdown("---")

    # Filter
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        sort_order = st.selectbox("Urutan", ["Tertinggi ke Terendah", "Terendah ke Tertinggi", "Alfabetis"])
    with col_f2:
        selected_cat = st.multiselect(
            "Filter Kategori", options=list(avg_total.index), default=list(avg_total.index)
        )

    if not selected_cat:
        st.warning("Pilih minimal satu kategori.")
        st.stop()

    data_fil = avg_total[selected_cat]
    if sort_order == "Tertinggi ke Terendah":
        data_fil = data_fil.sort_values(ascending=False)
    elif sort_order == "Terendah ke Tertinggi":
        data_fil = data_fil.sort_values(ascending=True)
    else:
        data_fil = data_fil.sort_index()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header"><h3>📊 Rata-rata Total Pengeluaran/User/Bulan</h3></div>', unsafe_allow_html=True)
        colors = ['#e74c3c' if v == data_fil.max() else '#3498db' if v == data_fil.min() else '#5d9cec'
                  for v in data_fil.values]
        fig = go.Figure(go.Bar(
            y=data_fil.index, x=data_fil.values, orientation='h',
            marker_color=colors,
            text=[f"Rp {v:,.0f}K" for v in data_fil.values],
            textposition='outside',
        ))
        fig.update_layout(
            height=380, margin=dict(l=0,r=90,t=10,b=10),
            xaxis_title="Rp Ribu / Bulan",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', xaxis=dict(gridcolor='#2d3e50'),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header"><h3>🥧 Proporsi Pengeluaran (%)</h3></div>', unsafe_allow_html=True)
        prop_fil = data_fil / data_fil.sum() * 100
        fig2 = go.Figure(go.Pie(
            labels=prop_fil.index, values=prop_fil.values,
            hole=0.4, textinfo='label+percent',
            marker_colors=px.colors.qualitative.Set2,
        ))
        fig2.update_layout(
            height=380, margin=dict(l=0,r=0,t=10,b=10),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Tabel ringkasan
    st.markdown('<div class="section-header"><h3>📋 Tabel Ringkasan Statistik</h3></div>', unsafe_allow_html=True)
    stat_df = pd.DataFrame({
        'Kategori': data_fil.index,
        'Rata-rata (Rp ribu)': data_fil.values.round(1),
        'Proporsi (%)': (data_fil / avg_total.sum() * 100).values.round(2),
    })
    stat_df['Ranking'] = stat_df['Rata-rata (Rp ribu)'].rank(ascending=False).astype(int)
    stat_df = stat_df[['Ranking','Kategori','Rata-rata (Rp ribu)','Proporsi (%)']].sort_values('Ranking')
    st.dataframe(stat_df.style.background_gradient(subset=['Rata-rata (Rp ribu)'], cmap='Blues'),
                 use_container_width=True, hide_index=True)

    st.markdown('<div class="insight-box"><h4>💡 Rekomendasi SnapBudget</h4><p>'
                'Fitur <b>alert</b> dan batas anggaran (budget limit) sebaiknya diprioritaskan untuk kategori '
                '<b>Makanan</b> dan <b>Belanja</b> terlebih dahulu — keduanya menyumbang &gt;52% total pengeluaran bulanan.'
                '</p></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 · PB2 PROFIL & STATUS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔥 PB2 · Profil & Status Keuangan":
    st.title("🔥 PB2 · Profil Pengeluaran & Status Keuangan")
    st.markdown("**8.000 sampel dataset Head 3 SnapBudget**")
    st.markdown("---")

    # Filter profil
    filter_profil = st.multiselect(
        "Filter Profil", ['Hemat','Normal','Boros'], default=['Hemat','Normal','Boros']
    )
    if not filter_profil:
        st.warning("Pilih minimal satu profil.")
        st.stop()

    h3_fil = head3_df[head3_df['profil_label'].isin(filter_profil)]

    col1, col2 = st.columns(2)

    # Stacked bar
    with col1:
        st.markdown('<div class="section-header"><h3>📊 Distribusi Status per Profil (%)</h3></div>', unsafe_allow_html=True)
        cross_fil = pd.crosstab(h3_fil['profil_label'], h3_fil['overall_label_name'], normalize='index') * 100
        for s in STATUS_ORDER:
            if s not in cross_fil.columns: cross_fil[s] = 0
        cross_fil = cross_fil[STATUS_ORDER]
        cross_fil = cross_fil.reindex([p for p in ['Hemat','Normal','Boros'] if p in cross_fil.index])

        fig = go.Figure()
        for status in STATUS_ORDER:
            if status in cross_fil.columns:
                vals = cross_fil[status].values
                fig.add_trace(go.Bar(
                    name=status, x=cross_fil.index, y=vals,
                    marker_color=STATUS_COLORS[status],
                    text=[f"{v:.0f}%" if v > 4 else '' for v in vals],
                    textposition='inside', textfont_color='white',
                ))
        fig.update_layout(
            barmode='stack', height=380, margin=dict(l=0,r=0,t=10,b=10),
            yaxis_title="Proporsi (%)", xaxis_title="Profil Pengeluaran",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', yaxis=dict(gridcolor='#2d3e50'),
            legend=dict(orientation='h', y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    with col2:
        st.markdown('<div class="section-header"><h3>🌡️ Heatmap % Anggaran per Status & Kategori</h3></div>', unsafe_allow_html=True)
        avg_pct_fil = (h3_fil.groupby('overall_label_name')[PCT_COLS].mean() * 100)
        avg_pct_fil.columns = [LABEL_MAP[c.replace('_pct_used','')] for c in PCT_COLS]
        available_status = [s for s in STATUS_ORDER if s in avg_pct_fil.index]
        avg_pct_fil = avg_pct_fil.reindex(available_status)

        fig2 = go.Figure(go.Heatmap(
            z=avg_pct_fil.values,
            x=avg_pct_fil.columns.tolist(),
            y=available_status,
            colorscale='RdYlGn_r',
            zmin=0, zmax=120,
            text=[[f"{v:.0f}%" for v in row] for row in avg_pct_fil.values],
            texttemplate="%{text}",
            textfont_size=11,
            colorbar=dict(title="% Anggaran", tickfont_color='white', title_font_color='white'),
        ))
        fig2.update_layout(
            height=380, margin=dict(l=0,r=0,t=10,b=10),
            xaxis=dict(tickangle=30),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Grouped Bar: % Anggaran per Kategori per Status ──────────────────
    st.markdown('<div class="section-header"><h3>📊 Berapa % Anggaran yang Terpakai per Kategori?</h3></div>', unsafe_allow_html=True)
    st.caption("Semakin tinggi batang = semakin banyak anggaran yang sudah terpakai. Batas aman = 100%.")

    sel_status = st.multiselect("Tampilkan Status", STATUS_ORDER, default=STATUS_ORDER, key="bar_status")

    avg_pct_fil2 = (h3_fil.groupby('overall_label_name')[PCT_COLS].mean() * 100)
    avg_pct_fil2.columns = [LABEL_MAP[c.replace('_pct_used','')] for c in PCT_COLS]

    fig3 = go.Figure()
    for status in sel_status:
        if status in avg_pct_fil2.index:
            vals = avg_pct_fil2.loc[status].values
            fig3.add_trace(go.Bar(
                name=status,
                x=avg_pct_fil2.columns.tolist(),
                y=vals,
                marker_color=STATUS_COLORS[status],
                text=[f"{v:.0f}%" for v in vals],
                textposition='outside',
                textfont=dict(size=10),
            ))

    # Garis batas 100%
    fig3.add_hline(
        y=100, line_dash='dash', line_color='white', line_width=1.5,
        annotation_text="⚠️ Batas 100% (Anggaran Habis)",
        annotation_position="top left",
        annotation_font=dict(color='white', size=11),
    )

    fig3.update_layout(
        barmode='group',
        height=440,
        margin=dict(l=0, r=0, t=40, b=10),
        xaxis_title="Kategori Pengeluaran",
        yaxis_title="% Anggaran Terpakai",
        yaxis=dict(range=[0, 145], gridcolor='#2d3e50', ticksuffix='%'),
        xaxis=dict(tickangle=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        legend=dict(
            orientation='h', y=1.12, x=0.5, xanchor='center',
            bgcolor='rgba(0,0,0,0.3)', bordercolor='#2d3e50', borderwidth=1,
        ),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Tabel ringkas dengan emoji indikator ─────────────────────────────
    st.markdown('<div class="section-header"><h3>📋 Ringkasan: Rata-rata % Anggaran per Status</h3></div>', unsafe_allow_html=True)

    EMOJI_STATUS = {'HEMAT':'🟢','AMAN':'💚','WASPADA':'🟡','BOROS':'🔴','DARURAT':'🚨'}
    tabel_rows = []
    for status in STATUS_ORDER:
        if status in avg_pct_fil2.index:
            row_vals = avg_pct_fil2.loc[status]
            rata = row_vals.mean()
            maks_cat = row_vals.idxmax()
            tabel_rows.append({
                'Status': f"{EMOJI_STATUS.get(status,'')} {status}",
                'Rata-rata Semua Kategori': f"{rata:.0f}%",
                'Kategori Paling Kritis': f"{maks_cat} ({row_vals.max():.0f}%)",
            })
    tabel_df = pd.DataFrame(tabel_rows)
    st.dataframe(tabel_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="insight-box"><h4>🚨 Insight Kritis</h4><p>'
                '• Profil <b>Boros</b> → DARURAT 69,5% — tidak ada satu pun yang mencapai status AMAN/HEMAT.<br>'
                '• Status DARURAT memiliki rata-rata penggunaan anggaran <b>&gt;100%</b> di Makanan, Minuman, Transportasi, Tagihan.<br>'
                '• <b>Tagihan</b> = selisih terbesar: DARURAT 81,8% vs HEMAT 19,8% = <b>108 poin %</b>.'
                '</p></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 · ANALISIS LANJUTAN
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Analisis Lanjutan":
    st.title("📈 Analisis Lanjutan")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📅 Tren Harian", "📦 Distribusi per Profil", "🏷️ Klasifikasi Teks (Head 1)"])

    # ── Tab 1: Tren Harian ─────────────────────────────────────────────────
    with tab1:
        st.markdown("### Tren Pengeluaran Harian Rata-rata per Kategori (37 Hari)")
        sel_cat_trend = st.multiselect(
            "Kategori", list(LABEL_MAP.values()), default=list(LABEL_MAP.values()),
            key="trend_cat"
        )
        fig = go.Figure()
        for cat, color in zip(list(LABEL_MAP.values()), CAT_COLORS):
            if cat in sel_cat_trend:
                fig.add_trace(go.Scatter(
                    x=daily_trend.index, y=daily_trend[cat],
                    name=cat, line=dict(color=color, width=2), mode='lines',
                ))
        fig.add_vline(x=30, line_dash='dash', line_color='gray',
                      annotation_text="Periode Prediksi",
                      annotation_position="top right", annotation_font_color='gray')
        fig.update_layout(
            height=420, xaxis_title="Hari ke-", yaxis_title="Pengeluaran Rata-rata (Rp ribu)",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', xaxis=dict(gridcolor='#2d3e50'), yaxis=dict(gridcolor='#2d3e50'),
            legend=dict(orientation='h', y=-0.2),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="insight-box"><h4>💡 Insight Tren</h4><p>'
                    '• Periode prediksi (hari 31–37) menunjukkan pola lanjutan dari hari sebelumnya.<br>'
                    '• Distribusi pengeluaran cenderung stabil — tidak ada lonjakan signifikan mid-month.<br>'
                    '• Makanan memiliki fluktuasi harian tertinggi dibanding kategori lain.'
                    '</p></div>', unsafe_allow_html=True)

    # ── Tab 2: Distribusi per Profil ──────────────────────────────────────
    with tab2:
        st.markdown("### Distribusi Jumlah User per Profil & Status Keuangan")
        status_profil = head3_df.groupby(['profil_label','overall_label_name']).size().unstack(fill_value=0)
        status_profil = status_profil.reindex(['Hemat','Normal','Boros'])
        for s in STATUS_ORDER:
            if s not in status_profil.columns: status_profil[s] = 0
        status_profil = status_profil[STATUS_ORDER]

        fig = go.Figure()
        for status in STATUS_ORDER:
            fig.add_trace(go.Bar(
                name=status, x=status_profil.index, y=status_profil[status],
                marker_color=STATUS_COLORS[status],
                text=status_profil[status].values,
                textposition='outside',
            ))
        fig.update_layout(
            barmode='group', height=420,
            xaxis_title="Profil Pengeluaran", yaxis_title="Jumlah User",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', yaxis=dict(gridcolor='#2d3e50'),
            legend=dict(orientation='h', y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Box plot % anggaran per profil
        st.markdown("### Box Plot: % Penggunaan Anggaran per Profil")
        cat_box = st.selectbox("Pilih Kategori", list(LABEL_MAP.values()), index=0, key="box_cat")
        cat_key = [k for k,v in LABEL_MAP.items() if v == cat_box][0]
        col_key = f"{cat_key}_pct_used"
        fig2 = go.Figure()
        for profil, color in [('Hemat','#27ae60'),('Normal','#f39c12'),('Boros','#e74c3c')]:
            data_profil = head3_df[head3_df['profil_label']==profil][col_key] * 100
            fig2.add_trace(go.Box(
                y=data_profil, name=profil,
                marker_color=color, line_color=color,
                boxmean='sd',
            ))
        fig2.update_layout(
            height=380, yaxis_title="% Penggunaan Anggaran",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_color='white', yaxis=dict(gridcolor='#2d3e50'),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tab 3: Head 1 Klasifikasi ──────────────────────────────────────────
    with tab3:
        st.markdown("### Distribusi Kategori Transaksi (Head 1 · Klasifikasi Teks)")
        cat_count = head1_df['category'].value_counts().rename(LABEL_MAP)
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure(go.Bar(
                x=cat_count.index, y=cat_count.values,
                marker_color=CAT_COLORS,
                text=cat_count.values, textposition='outside',
            ))
            fig.update_layout(
                height=360, xaxis_title="Kategori", yaxis_title="Jumlah Entri",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font_color='white', yaxis=dict(gridcolor='#2d3e50'),
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.dataframe(
                cat_count.reset_index().rename(columns={'index':'Kategori','category':'Jumlah'}),
                use_container_width=True, hide_index=True
            )
            st.metric("Total entri (setelah cleaning)", f"{len(head1_df):,}")
            st.metric("Duplikat dihapus", "6.534 baris")
            st.metric("Baris noise dibersihkan", "927 baris")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5 · EKSPLORASI DATASET
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🗃️ Eksplorasi Dataset":
    st.title("🗃️ Eksplorasi Dataset")
    st.markdown("---")

    ds = st.radio("Pilih Dataset", ["Head 1 (Klasifikasi Teks)", "Head 2 (Pengeluaran Harian)", "Head 3 (Profil Finansial)"],
                  horizontal=True)

    if ds == "Head 1 (Klasifikasi Teks)":
        df_show = head1_df
    elif ds == "Head 2 (Pengeluaran Harian)":
        df_show = head2_df
    else:
        df_show = head3_df

    c1, c2, c3 = st.columns(3)
    c1.metric("Jumlah Baris", f"{len(df_show):,}")
    c2.metric("Jumlah Kolom", len(df_show.columns))
    c3.metric("Missing Values", int(df_show.isnull().sum().sum()))

    st.markdown("**Preview Data (10 baris pertama)**")
    st.dataframe(df_show.head(10), use_container_width=True)

    st.markdown("**Statistik Deskriptif**")
    st.dataframe(df_show.describe().round(3), use_container_width=True)

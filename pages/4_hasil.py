import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def show_hasil():
    st.title("Hasil Analisis Klasterisasi dan Anomali")
    
    if 'analysis_results' not in st.session_state:
        st.warning("Silakan jalankan analisis terlebih dahulu di halaman Perhitungan")
        return
    
    results = st.session_state.analysis_results
    tahun = st.session_state.analysis_year
    result_df = results['results']
    
    st.subheader(f"Hasil Analisis - Tahun {tahun}")
    
    # **PERBAIKAN COLOR CELL YANG LEBIH JELAS**
    def highlight_cluster(val):
        """Highlight cell berdasarkan klaster dengan kontras yang baik"""
        if val == 'Anomali':
            return 'background-color: #ff6b6b; color: white; font-weight: bold;'
        elif val == 'Tinggi':
            return 'background-color: #4CAF50; color: white; font-weight: bold;'
        elif val == 'Sedang':
            return 'background-color: #FFA726; color: black; font-weight: bold;'
        elif val == 'Rendah':
            return 'background-color: #EF5350; color: white; font-weight: bold;'
        return ''
    
    # Format tahun tanpa koma
    display_df = result_df.copy()
    display_df['Tahun'] = display_df['Tahun'].astype(int)
    
    # Rename kolom dengan satuan
    display_df = display_df.rename(columns={
        'Luas_Panen': 'Luas Panen (Ha)',
        'Produksi': 'Produksi (Ton)',
        'Produktivitas': 'Produktivitas (Ton/Ha)',
        'Skor_Anomali': 'Skor Anomali'
    })
    
    # Apply styling
    styled_df = display_df.style.applymap(highlight_cluster, subset=['Klaster'])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Download hasil
    csv = result_df.to_csv(index=False)
    st.download_button(
        label="Download Hasil Analisis (CSV)",
        data=csv,
        file_name=f"hasil_analisis_{tahun}.csv",
        mime="text/csv"
    )
    
    # Visualisasi
    st.subheader("📈 Visualisasi Hasil")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart dengan warna yang lebih kontras
        st.write("**Distribusi Klaster**")
        
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        klaster_count = result_df['Klaster'].value_counts()
        
        # **PERBAIKAN WARNA LEBIH KONTRAST**
        colors = {
            'Tinggi': '#27ae60',    # Hijau tua
            'Sedang': '#f39c12',    # Orange tua  
            'Rendah': '#e74c3c',    # Merah tua
            'Anomali': '#8e44ad'    # Ungu tua
        }
        color_list = [colors.get(k, '#7f8c8d') for k in klaster_count.index]
        
        wedges, texts, autotexts = ax1.pie(
            klaster_count.values, 
            labels=klaster_count.index,
            autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100.*sum(klaster_count.values))})',
            colors=color_list,
            startangle=90,
            textprops={'fontsize': 10, 'fontweight': 'bold'}
        )
        
        # **PERBAIKAN TEKS LEBIH JELAS**
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        for text in texts:
            text.set_fontweight('bold')
            text.set_fontsize(11)
        
        ax1.set_title('Distribusi Klaster dan Anomali', fontweight='bold', fontsize=12)
        st.pyplot(fig1)
    
    with col2:
        # Bar chart produktivitas dengan warna yang lebih kontras
        st.write("**Produktivitas per Kecamatan**")
        
        # Urutkan berdasarkan produktivitas
        sorted_df = result_df.sort_values('Produktivitas', ascending=False)
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        
        # **PERBAIKAN WARNA BAR CHART**
        colors_bar = {
            'Tinggi': '#27ae60',    # Hijau tua
            'Sedang': '#f39c12',    # Orange tua
            'Rendah': '#e74c3c',    # Merah tua
            'Anomali': '#8e44ad'    # Ungu tua
        }
        bar_colors = [colors_bar.get(klaster, '#95a5a6') for klaster in sorted_df['Klaster']]
        
        bars = ax2.bar(range(len(sorted_df)), sorted_df['Produktivitas'], 
                      color=bar_colors, edgecolor='black', linewidth=0.5)
        
        # **PERBAIKAN LABEL LEBIH JELAS**
        ax2.set_ylabel('Produktivitas (Ton/Ha)', fontweight='bold', fontsize=11)
        ax2.set_xlabel('Kecamatan', fontweight='bold', fontsize=11)
        ax2.set_title('Produktivitas per Kecamatan (Diurutkan)', 
                     fontweight='bold', fontsize=12)
        
        # Rotasi label untuk kejelasan
        ax2.set_xticks(range(len(sorted_df)))
        ax2.set_xticklabels(sorted_df['Kecamatan'], rotation=45, ha='right', fontsize=9)
        
        # Grid untuk readability
        ax2.grid(True, axis='y', alpha=0.3, linestyle='--')
        
        # **PERBAIKAN LEGEND LEBIH JELAS**
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=colors_bar['Tinggi'], edgecolor='black', label='Tinggi'),
            Patch(facecolor=colors_bar['Sedang'], edgecolor='black', label='Sedang'),
            Patch(facecolor=colors_bar['Rendah'], edgecolor='black', label='Rendah'),
            Patch(facecolor=colors_bar['Anomali'], edgecolor='black', label='Anomali')
        ]
        ax2.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    # Scatter plot untuk melihat hubungan
    st.subheader("🔍 Analisis Hubungan Variabel")
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    # **PERBAIKAN WARNA SCATTER PLOT**
    colors_scatter = {
        'Tinggi': '#27ae60',
        'Sedang': '#f39c12', 
        'Rendah': '#e74c3c',
        'Anomali': '#8e44ad'
    }
    
    for klaster in colors_scatter.keys():
        cluster_data = result_df[result_df['Klaster'] == klaster]
        if len(cluster_data) > 0:
            ax3.scatter(
                cluster_data['Luas_Panen'], 
                cluster_data['Produktivitas'],
                c=colors_scatter[klaster],
                label=klaster,
                alpha=0.8,
                s=120,
                edgecolor='black',
                linewidth=0.5
            )
    
    ax3.set_xlabel('Luas Panen (Ha)', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Produktivitas (Ton/Ha)', fontweight='bold', fontsize=11)
    ax3.set_title('Hubungan Luas Panen vs Produktivitas', fontweight='bold', fontsize=12)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--')
    st.pyplot(fig3)
    
    # **STATISTIK DETAIL**
    st.subheader("📊 Statistik Detail per Klaster")
    
    # **PERBAIKAN WARNA BACKGROUND EXPANDER**
    expander_styles = {
        'Tinggi': {'background': '#d5f4e6', 'border': '2px solid #27ae60'},
        'Sedang': {'background': '#fff3cd', 'border': '2px solid #f39c12'},
        'Rendah': {'background': '#f8d7da', 'border': '2px solid #e74c3c'},
        'Anomali': {'background': '#e8d6ff', 'border': '2px solid #8e44ad'}
    }
    
    for klaster in ['Tinggi', 'Sedang', 'Rendah', 'Anomali']:
        cluster_data = result_df[result_df['Klaster'] == klaster]
        
        if len(cluster_data) > 0:
            # **PERBAIKAN TAMPILAN EXPANDER**
            with st.expander(f"📋 **{klaster}** ({len(cluster_data)} kecamatan)"):
                # Tambahkan custom CSS untuk expander
                st.markdown(f"""
                <style>
                .st-expander {{
                    border: {expander_styles[klaster]['border']} !important;
                    background-color: {expander_styles[klaster]['background']} !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rata-rata Produktivitas", f"{cluster_data['Produktivitas'].mean():.3f} Ton/Ha")
                with col2:
                    st.metric("Total Produksi", f"{cluster_data['Produksi'].sum():,.0f} Ton")
                with col3:
                    st.metric("Rata-rata Luas Panen", f"{cluster_data['Luas_Panen'].mean():.1f} Ha")
                
                st.write(f"**Kecamatan:** {', '.join(cluster_data['Kecamatan'].tolist())}")
                
                # Rekomendasi
                if klaster == 'Tinggi':
                    st.success("**✅ REKOMENDASI:** Pertahankan kinerja excellent, dapat dijadikan percontohan untuk kecamatan lain.")
                elif klaster == 'Sedang':
                    st.info("**💡 REKOMENDASI:** Tingkatkan melalui optimalisasi input pertanian dan manajemen yang lebih baik.")
                elif klaster == 'Rendah':
                    st.warning("**⚠️ REKOMENDASI:** Perlu intervensi khusus, evaluasi menyeluruh faktor produksi dan kondisi lahan.")
                elif klaster == 'Anomali':
                    st.error("**🔍 REKOMENDASI:** Perlu investigasi mendalam dan verifikasi data lapangan.")
    
    # **INFO TEKNIS**
    st.subheader("⚙️ Informasi Teknis Analisis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Silhouette Score", f"{results['silhouette_score']:.3f}")
        st.metric("Jumlah Anomali", results['anomaly_count'])
    
    with col2:
        st.metric("Total Data", len(result_df))
        st.metric("Features Used", ", ".join(results.get('features_used', ['Produktivitas'])))

if __name__ == "__main__":
    if st.session_state.get('authenticated', False):
        show_hasil()
    else:
        st.warning("Silakan login terlebih dahulu.")
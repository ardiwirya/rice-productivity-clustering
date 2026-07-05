import streamlit as st
import numpy as np
from utils.data_loader import DataLoader
from utils.anomaly_detector import AnomalyDetector

def show_perhitungan():
    st.title("Analisis Klasterisasi dan Anomali")
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    loader = st.session_state.data_loader
    yearly_data = loader.get_yearly_data()
    
    if yearly_data.empty:
        st.error("Tidak ada data untuk dianalisis")
        return
    
    st.subheader("Parameter Analisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pilih tahun
        tahun_options = sorted(yearly_data['Tahun'].unique())
        selected_year = st.selectbox("Pilih Tahun untuk Analisis", tahun_options)
        
        # **TAMBAHAN BARU**: Pilih metode analisis
        analysis_method = st.radio(
            "Metode Analisis",
            ["Standard", "Enhanced"],
            help="Standard: hanya produktivitas. Enhanced: multiple features"
        )
        
    with col2:
        # **PARAMETER YANG LEBIH FLEKSIBEL**
        contamination = st.slider(
            "Tingkat Kontaminasi (anomali)", 
            0.05, 0.3, 0.15, 0.01,
            help="Persentase data yang dianggap anomali (5-30%)"
        )
        
        n_estimators = st.slider(
            "Jumlah Estimator", 
            50, 300, 150, 10,
            help="Kompleksitas model (50-300)"
        )
    
    # Opsi tambahan (nonaktif secara default, karena ini mengubah data asli
    # sebelum dianalisis - hanya berguna untuk demo dengan dataset yang
    # sangat homogen)
    st.subheader("Opsi Tambahan")
    add_variation = st.checkbox(
        "Tambah variasi data (demo only)",
        value=False,
        help="Menambah noise acak kecil pada produktivitas sebelum dianalisis. "
             "Nonaktif secara default agar hasil analisis mencerminkan data asli."
    )

    # Filter data
    analysis_data = yearly_data[yearly_data['Tahun'] == selected_year].copy()

    if analysis_data.empty:
        st.error("Tidak ada data untuk tahun yang dipilih")
        return

    if add_variation and len(analysis_data) > 0:
        variation = np.random.normal(1.0, 0.02, len(analysis_data))
        analysis_data['Produktivitas'] = analysis_data['Produktivitas'] * variation
        st.caption("⚠️ Data produktivitas sedang dimodifikasi dengan noise acak untuk keperluan demo.")
    
    st.subheader("Data yang Akan Dianalisis")
    
    # Tampilkan statistik data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jumlah Data", len(analysis_data))
    with col2:
        st.metric("Rata-rata Produktivitas", f"{analysis_data['Produktivitas'].mean():.3f} Ton/Ha")
    with col3:
        st.metric("Std Dev Produktivitas", f"{analysis_data['Produktivitas'].std():.3f}")
    with col4:
        st.metric("Range Produktivitas", 
                 f"{analysis_data['Produktivitas'].min():.2f}-{analysis_data['Produktivitas'].max():.2f}")
    
    st.dataframe(analysis_data[['Kecamatan', 'Produktivitas', 'Luas_Panen', 'Produksi']], 
                 use_container_width=True)
    
    if st.button("Jalankan Analisis", type="primary"):
        with st.spinner("Menjalankan analisis..."):
            try:
                detector = AnomalyDetector(
                    n_estimators=n_estimators,
                    contamination=contamination
                )
                
                results = detector.analyze_data(analysis_data)
                
                if results:
                    st.session_state.analysis_results = results
                    st.session_state.analysis_year = selected_year
                    
                    st.success("Analisis berhasil!")
                    
                    # Tampilkan hasil ringkas yang lebih informatif
                    result_df = results['results']
                    
                    st.subheader("📊 Hasil Analisis")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Data", len(result_df))
                    with col2:
                        anomali_count = len(result_df[result_df['Klaster'] == 'Anomali'])
                        st.metric("Anomali Terdeteksi", anomali_count)
                    with col3:
                        silhouette = results['silhouette_score']
                        st.metric("Silhouette Score", f"{silhouette:.3f}")
                    with col4:
                        # Hitung distribusi klaster
                        klaster_counts = result_df['Klaster'].value_counts()
                        display_text = "\n".join([f"{k}: {v}" for k, v in klaster_counts.items()])
                        st.metric("Distribusi Klaster", display_text)
                    
                    # Tampilkan features yang digunakan
                    st.info(f"Features yang digunakan: {', '.join(results['features_used'])}")
                    
                    # **TAMBAHAN**: Tampilkan skor anomali
                    st.subheader("Distribusi Skor Anomali")
                    if anomali_count > 0:
                        anomali_scores = result_df[result_df['Klaster'] == 'Anomali']['Skor_Anomali']
                        st.write(f"Skor anomali terendah: {anomali_scores.min():.4f}")
                        st.write(f"Skor anomali tertinggi: {anomali_scores.max():.4f}")
                    
            except Exception as e:
                st.error(f"Error dalam analisis: {e}")
                st.info("Coba ubah parameter atau aktifkan 'Tambah variasi data'")

if __name__ == "__main__":
    if st.session_state.get('authenticated', False):
        show_perhitungan()
    else:
        st.warning("Silakan login terlebih dahulu.")
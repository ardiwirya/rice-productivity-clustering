import streamlit as st
from utils.data_loader import DataLoader

def show_dashboard():
    st.title("Dashboard Analisis Produktivitas Padi")
    
    # Load data sekali saja
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    loader = st.session_state.data_loader
    yearly_data = loader.get_yearly_data()
    
    if yearly_data.empty:
        st.error("Tidak ada data yang dapat dimuat")
        return
    
    # Statistik
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Kecamatan", yearly_data['Kecamatan'].nunique())
    with col2:
        st.metric("Rata-rata Produktivitas", f"{yearly_data['Produktivitas'].mean():.2f} Ton/Ha")
    with col3:
        st.metric("Tahun Tersedia", f"{int(yearly_data['Tahun'].min())} - {int(yearly_data['Tahun'].max())}")
    with col4:
        st.metric("Total Data", len(yearly_data))
    
    # Data preview
    st.subheader("Data Produktivitas Padi (2020-2024)")
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        tahun_filter = st.selectbox("Filter Tahun", ['All'] + sorted(yearly_data['Tahun'].unique().tolist()))
    with col2:
        kecamatan_filter = st.selectbox("Filter Kecamatan", ['All'] + sorted(yearly_data['Kecamatan'].unique().tolist()))
    
    # Apply filter
    filtered_data = yearly_data.copy()
    if tahun_filter != 'All':
        filtered_data = filtered_data[filtered_data['Tahun'] == tahun_filter]
    if kecamatan_filter != 'All':
        filtered_data = filtered_data[filtered_data['Kecamatan'] == kecamatan_filter]
    
    # Format tahun tanpa koma
    display_data = filtered_data.copy()
    display_data['Tahun'] = display_data['Tahun'].astype(int)
    
    # Rename kolom dengan satuan
    display_data = display_data.rename(columns={
        'Luas_Panen': 'Luas Panen (Ha)',
        'Produksi': 'Produksi (Ton)',
        'Produktivitas': 'Produktivitas (Ton/Ha)'
    })
    
    st.dataframe(display_data, use_container_width=True)
    
    # Tren tahunan
    st.subheader("Tren Produktivitas per Tahun")
    yearly_avg = yearly_data.groupby('Tahun')['Produktivitas'].mean().reset_index()
    yearly_avg['Tahun'] = yearly_avg['Tahun'].astype(int)  # Hilangkan koma
    st.line_chart(yearly_avg.set_index('Tahun'))

if __name__ == "__main__":
    if st.session_state.get('authenticated', False):
        show_dashboard()
    else:
        st.warning("Silakan login terlebih dahulu.")
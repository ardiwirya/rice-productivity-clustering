import streamlit as st
from utils.data_loader import DataLoader

def show_data():
    st.title("Data Produktivitas Padi")
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    loader = st.session_state.data_loader
    yearly_data = loader.get_yearly_data()
    monthly_data = loader.get_monthly_data()
    
    tab1, tab2 = st.tabs(["Data Tahunan", "Data Bulanan"])
    
    with tab1:
        st.subheader("Data Tahunan (Agregat)")
        
        if yearly_data.empty:
            st.error("Tidak ada data tahunan yang dapat dimuat")
        else:
            st.success(f"✅ Data berhasil dimuat: {len(yearly_data)} records")
            st.info(f"Tahun tersedia: {int(min(yearly_data['Tahun']))} - {int(max(yearly_data['Tahun']))}")
            st.info(f"Jumlah kecamatan: {yearly_data['Kecamatan'].nunique()}")
            
            # Filter
            col1, col2 = st.columns(2)
            with col1:
                tahun_filter = st.selectbox("Filter Tahun", 
                                          ['All'] + sorted(yearly_data['Tahun'].unique().tolist()))
            with col2:
                kecamatan_filter = st.selectbox("Filter Kecamatan", 
                                              ['All'] + sorted(yearly_data['Kecamatan'].unique().tolist()))
            
            # Apply filter
            filtered_data = yearly_data.copy()
            if tahun_filter != 'All':
                filtered_data = filtered_data[filtered_data['Tahun'] == tahun_filter]
            if kecamatan_filter != 'All':
                filtered_data = filtered_data[filtered_data['Kecamatan'] == kecamatan_filter]
            
            # Format untuk display
            display_data = filtered_data.copy()
            display_data['Tahun'] = display_data['Tahun'].astype(int)
            
            # Rename kolom dengan satuan
            display_data = display_data.rename(columns={
                'Luas_Panen': 'Luas Panen (Ha)',
                'Produksi': 'Produksi (Ton)',
                'Produktivitas': 'Produktivitas (Ton/Ha)'
            })
            
            st.dataframe(display_data, use_container_width=True)
            
            # Statistik
            st.subheader("Statistik")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rata-rata Produktivitas", f"{filtered_data['Produktivitas'].mean():.2f} Ton/Ha")
            with col2:
                st.metric("Total Produksi", f"{filtered_data['Produksi'].sum():,.0f} Ton")
            with col3:
                st.metric("Total Luas Panen", f"{filtered_data['Luas_Panen'].sum():,.0f} Ha")
            with col4:
                st.metric("Jumlah Data", len(filtered_data))
            
            # Download
            csv = yearly_data.to_csv(index=False)
            st.download_button(
                label="Download Data Tahunan (CSV)",
                data=csv,
                file_name="data_tahunan_padi.csv",
                mime="text/csv"
            )
    
    with tab2:
        st.subheader("Data Bulanan (Detail)")
        
        if monthly_data.empty:
            st.warning("Data bulanan tidak tersedia atau format file tidak sesuai")
            
            # Tampilkan sample data tahunan
            if not yearly_data.empty:
                st.subheader("Data Tahunan yang Tersedia")
                display_yearly = yearly_data.copy()
                display_yearly['Tahun'] = display_yearly['Tahun'].astype(int)
                display_yearly = display_yearly.rename(columns={
                    'Luas_Panen': 'Luas Panen (Ha)',
                    'Produksi': 'Produksi (Ton)',
                    'Produktivitas': 'Produktivitas (Ton/Ha)'
                })
                st.dataframe(display_yearly.head(10), use_container_width=True)
        else:
            st.success(f"✅ Data bulanan tersedia: {len(monthly_data)} records")
            
            # Filter data bulanan
            col1, col2, col3 = st.columns(3)
            with col1:
                tahun_filter = st.selectbox("Tahun", 
                                          ['All'] + sorted(monthly_data['Tahun'].unique().tolist()),
                                          key='bulan_tahun')
            with col2:
                kecamatan_filter = st.selectbox("Kecamatan", 
                                              ['All'] + sorted(monthly_data['Kecamatan'].unique().tolist()),
                                              key='bulan_kecamatan')
            with col3:
                bulan_filter = st.selectbox("Bulan", 
                                          ['All'] + sorted(monthly_data['Bulan'].unique().tolist()),
                                          key='bulan_filter')
            
            filtered_monthly = monthly_data.copy()
            if tahun_filter != 'All':
                filtered_monthly = filtered_monthly[filtered_monthly['Tahun'] == tahun_filter]
            if kecamatan_filter != 'All':
                filtered_monthly = filtered_monthly[filtered_monthly['Kecamatan'] == kecamatan_filter]
            if bulan_filter != 'All':
                filtered_monthly = filtered_monthly[filtered_monthly['Bulan'] == bulan_filter]
            
            # Format untuk display
            display_monthly = filtered_monthly.copy()
            display_monthly['Tahun'] = display_monthly['Tahun'].astype(int)
            
            # Rename kolom dengan satuan
            display_monthly = display_monthly.rename(columns={
                'Tanam': 'Luas Tanam (Ha)',
                'Panen': 'Luas Panen (Ha)',
                'Produksi': 'Produksi (Ton)',
                'Produktivitas': 'Produktivitas (Ton/Ha)'
            })
            
            st.dataframe(display_monthly, use_container_width=True)
            
            # Download data bulanan
            if not monthly_data.empty:
                csv_monthly = monthly_data.to_csv(index=False)
                st.download_button(
                    label="Download Data Bulanan (CSV)",
                    data=csv_monthly,
                    file_name="data_bulanan_padi.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    if st.session_state.get('authenticated', False):
        show_data()
    else:
        st.warning("Silakan login terlebih dahulu.")
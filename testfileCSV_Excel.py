import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rekap Order Source", layout="wide")
st.title("📊 Sales Dashboard Jumlah Data Berdasarkan Order Source")

# Upload file
uploaded_file = st.file_uploader("📁 Upload file (.xlsx or .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Deteksi jenis file dan baca
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        # Hapus kolom kosong dan duplikat
        df = df.dropna(axis=1, how='all')
        df = df.loc[:, ~df.columns.duplicated()]

        # Konversi kolom tanggal jika tersedia
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')

        st.subheader("✅ Data Awal yang Diunggah:")
        st.dataframe(df.head(10), use_container_width=True)

        # Filter Berdasarkan Tanggal (jika ada kolom 'Order Date')
        if 'Order Date' in df.columns:
            st.sidebar.subheader("📅 Filter Tanggal Order")
            min_date = df['Order Date'].min()
            max_date = df['Order Date'].max()
            start_date, end_date = st.sidebar.date_input("Rentang Tanggal", [min_date, max_date])
            df = df[(df['Order Date'] >= pd.to_datetime(start_date)) & (df['Order Date'] <= pd.to_datetime(end_date))]

        # Filter Berdasarkan Partner
        if 'Partner' in df.columns:
            partner_list = df['Partner'].dropna().unique().tolist()
            selected_partner = st.sidebar.multiselect("🏢 Filter Partner", partner_list, default=partner_list)
            df = df[df['Partner'].isin(selected_partner)]

        # Filter Berdasarkan Channel
        if 'Channel' in df.columns:
            channel_list = df['Channel'].dropna().unique().tolist()
            selected_channel = st.sidebar.multiselect("📡 Filter Channel", channel_list, default=channel_list)
            df = df[df['Channel'].isin(selected_channel)]

        # Filter Berdasarkan Order Source
        if 'Order Source' in df.columns:
            source_list = df['Order Source'].dropna().unique().tolist()
            selected_source = st.sidebar.multiselect("🛍️ Filter Order Source", source_list, default=source_list)
            df = df[df['Order Source'].isin(selected_source)]

        # Grouping dan Agregasi
        if 'Order Source' not in df.columns:
            st.error("❌ Kolom 'Order Source' tidak ditemukan.")
        else:
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                st.warning("Tidak ada kolom numerik untuk dihitung.")
            else:
                summary = df.groupby('Order Source')[numeric_cols].sum().reset_index()

                st.subheader("📈 Hasil Ringkasan per Order Source:")
                st.dataframe(summary, use_container_width=True)

                # Tombol download
                csv = summary.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download hasil (.csv)", csv, file_name="rekap_order_source.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat membaca file: {e}")

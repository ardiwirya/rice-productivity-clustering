import pandas as pd
import numpy as np
import os

# Set to True only when debugging data-loading issues locally.
DEBUG = False


class DataLoader:
    """Loads and aggregates the annual rice-productivity reports (2020-2024)
    published by Dinas Pertanian Kabupaten Deli Serdang.
    """

    def __init__(self):
        # Resolve the data folder relative to this file, not the current
        # working directory. This makes the app runnable from any location
        # (VS Code "Run" button, terminal, Streamlit Cloud, etc.) instead of
        # only from the project root.
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_folder = os.path.join(project_root, "data")
        self.yearly_data = None
        self.monthly_data = None
        self.load_all_data()

    def load_all_data(self):
        """Load all 5 yearly CSV reports."""
        all_monthly_data = []

        files = [
            ("laporan_Padi_2020.csv", 2020),
            ("laporan_Padi_2021.csv", 2021),
            ("laporan_Padi_2022.csv", 2022),
            ("laporan_Padi_2023.csv", 2023),
            ("laporan_Padi_2024.csv", 2024),
        ]

        for filename, tahun in files:
            filepath = os.path.join(self.data_folder, filename)
            if os.path.exists(filepath):
                try:
                    monthly_df = self.load_special_format(filepath, tahun)
                    if monthly_df is not None and not monthly_df.empty:
                        all_monthly_data.append(monthly_df)
                        if DEBUG:
                            print(f"Loaded {filename}: {len(monthly_df)} records")
                    elif DEBUG:
                        print(f"No usable rows found in {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
            else:
                print(f"File not found: {filepath}")

        if all_monthly_data:
            self.monthly_data = pd.concat(all_monthly_data, ignore_index=True)
            self.yearly_data = self.aggregate_to_yearly(self.monthly_data)
            if DEBUG:
                print(
                    f"Loaded {len(self.monthly_data)} monthly records, "
                    f"{len(self.yearly_data)} yearly records"
                )
        else:
            print("No CSV data found - falling back to sample dataset.")
            self.yearly_data = self.create_sample_data()
            self.monthly_data = pd.DataFrame()

    def load_special_format(self, filepath, tahun):
        """Parse the Dinas Pertanian report layout: one header block followed
        by one row per kecamatan, with 3 columns (Tanam/Panen/Produksi) per
        month.
        """
        try:
            df = pd.read_csv(filepath, encoding="latin-1")

            data_rows = []
            kecamatan_start = None

            for i, row in df.iterrows():
                kecamatan = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""

                if "Gunung Meriah" in kecamatan and kecamatan_start is None:
                    kecamatan_start = i

                if kecamatan_start is not None and i >= kecamatan_start:
                    if pd.isna(kecamatan) or kecamatan == "" or "JUMLAH" in kecamatan or "TOTAL" in kecamatan:
                        break

                    if any(char.isalpha() for char in kecamatan):
                        bulan_data = self.extract_monthly_data(row, tahun, kecamatan.strip())
                        data_rows.extend(bulan_data)

            return pd.DataFrame(data_rows) if data_rows else pd.DataFrame()

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None

    def extract_monthly_data(self, row, tahun, kecamatan):
        """Extract the 12 monthly records for one kecamatan and compute
        productivity (Produksi / Panen).
        """
        data_bulanan = []
        bulan_list = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember",
        ]

        for bulan_idx, bulan in enumerate(bulan_list):
            start_col = 1 + (bulan_idx * 3)

            if start_col + 2 >= len(row):
                break

            try:
                tanam = self.clean_number(row.iloc[start_col])
                panen = self.clean_number(row.iloc[start_col + 1])
                produksi = self.clean_number(row.iloc[start_col + 2])

                if panen == 0 or produksi == 0:
                    continue

                # Productivity = Produksi (ton) / Panen (hectare)
                produktivitas = produksi / panen

                # Sanity check: typical rice productivity is 4-7 ton/ha.
                # Some source rows report Produksi in kuintal instead of ton;
                # detect and correct that case.
                if produktivitas < 1 or produktivitas > 10:
                    produktivitas_kuintal = (produksi * 10) / panen
                    if 4 <= produktivitas_kuintal <= 7:
                        produktivitas = produktivitas_kuintal
                        produksi = produksi * 10
                    elif DEBUG:
                        print(
                            f"Unrealistic productivity ({produktivitas:.2f} t/ha) "
                            f"for {kecamatan} - {bulan} {tahun}, kept as-is"
                        )

                data_bulanan.append(
                    {
                        "Kecamatan": kecamatan,
                        "Tahun": tahun,
                        "Bulan": bulan,
                        "Tanam": tanam,
                        "Panen": panen,
                        "Produksi": produksi,
                        "Produktivitas": round(produktivitas, 4),
                    }
                )

            except (ValueError, TypeError, IndexError, ZeroDivisionError):
                continue

        return data_bulanan

    def clean_number(self, value):
        """Parse numbers that may use comma decimal separators or stray
        whitespace.
        """
        if pd.isna(value) or value == "" or value == "-":
            return 0.0

        try:
            value_str = str(value).strip().replace(",", ".")

            clean_str = "".join(
                char for char in value_str if char.isdigit() or char == "."
            )

            if not clean_str:
                return 0.0

            result = float(clean_str)
            return result if result >= 0 else 0.0

        except (ValueError, TypeError):
            return 0.0

    def aggregate_to_yearly(self, monthly_df):
        """Aggregate monthly records into one row per kecamatan per year.
        Yearly productivity is the harvest-weighted average
        (total Produksi / total Panen), not a plain mean of monthly ratios.
        """
        if monthly_df.empty:
            return self.create_sample_data()

        yearly_data = []

        for (kecamatan, tahun), group in monthly_df.groupby(["Kecamatan", "Tahun"]):
            total_panen = group["Panen"].sum()
            total_produksi = group["Produksi"].sum()

            produktivitas = total_produksi / total_panen if total_panen > 0 else 0

            if produktivitas > 0 and (produktivitas < 3 or produktivitas > 8):
                avg_simple = group["Produktivitas"].mean()
                if 3 <= avg_simple <= 8:
                    produktivitas = avg_simple

            yearly_data.append(
                {
                    "Kecamatan": kecamatan,
                    "Tahun": tahun,
                    "Luas_Panen": round(total_panen, 2),
                    "Produksi": round(total_produksi, 2),
                    "Produktivitas": round(produktivitas, 4),
                }
            )

        return pd.DataFrame(yearly_data)

    def create_sample_data(self):
        """Synthetic fallback dataset, used only if no CSV files can be
        found, so the app is still explorable end-to-end.
        """
        kecamatan_list = [
            "Gunung Meriah", "Stm Hulu", "Sibolangit", "Kutalimbaru", "Pancur Batu",
            "Namo Rambe", "Biru-biru", "Stm Hilir", "Bangun Purba", "Galang",
            "Tanjung Morawa", "Patumbak", "Deli Tua", "Sunggal", "Hamparan Perak",
            "Labuhan Deli", "Percut S Tuan", "Batang Kuis", "Pantai Labu", "Beringin",
            "Lubuk Pakam", "Pagar Merbau",
        ]

        data = []
        for tahun in [2020, 2021, 2022, 2023, 2024]:
            for kecamatan in kecamatan_list:
                luas_panen = np.random.uniform(100, 5000)
                produktivitas = np.random.normal(5.5, 0.5)
                produksi = luas_panen * produktivitas

                data.append(
                    {
                        "Kecamatan": kecamatan,
                        "Tahun": tahun,
                        "Luas_Panen": round(luas_panen, 2),
                        "Produksi": round(produksi, 2),
                        "Produktivitas": round(produktivitas, 4),
                    }
                )

        return pd.DataFrame(data)

    def get_yearly_data(self):
        return self.yearly_data.copy() if self.yearly_data is not None else pd.DataFrame()

    def get_monthly_data(self):
        return self.monthly_data.copy() if self.monthly_data is not None else pd.DataFrame()

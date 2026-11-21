import hashlib
import io
import os
import re
import zipfile
from collections import defaultdict
from datetime import datetime

import pandas as pd
import streamlit as st

# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(page_title="SORTIFY", page_icon="📁", layout="wide")

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
FILE_TYPES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".pptx", ".ppt", ".md"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff"],
    "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".sql", ".ipynb"],
}

ICONS = {
    "Documents": "📄", "Images": "🖼️", "Spreadsheets": "📊", "Videos": "🎬",
    "Audio": "🎵", "Archives": "🗜️", "Code": "💻", "Others": "📂",
}

STRUCTURES = {
    "Category  (Images/photo.jpg)": "category",
    "Category → Extension  (Images/JPG/photo.jpg)": "category_ext",
    "Category → Size  (Images/Small/photo.jpg)": "category_size",
}

MB = 1024 * 1024


# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def get_category(file_name: str) -> str:
    ext = os.path.splitext(file_name)[1].lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "Others"


def human_size(num_bytes: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}" if unit != "B" else f"{int(num_bytes)} B"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def size_bucket(size: int) -> str:
    if size < MB:
        return "Small (under 1MB)"
    if size < 10 * MB:
        return "Medium (1-10MB)"
    return "Large (over 10MB)"


def clean_name(name: str) -> str:
    base, ext = os.path.splitext(name)
    base = re.sub(r"[^\w\-. ]", "", base).strip()
    base = re.sub(r"\s+", "_", base).lower() or "file"
    return base + ext.lower()


def build_records(uploaded_files, clean_names: bool):
    """Read files once, compute hash, category, and duplicate flag."""
    records, seen_hashes = [], {}
    for f in uploaded_files:
        data = f.getvalue()
        digest = hashlib.sha256(data).hexdigest()
        name = clean_name(f.name) if clean_names else f.name
        ext = os.path.splitext(name)[1].lower()
        is_dup = digest in seen_hashes
        seen_hashes.setdefault(digest, name)
        records.append({
            "name": name,
            "original_name": f.name,
            "extension": ext or "(none)",
            "category": get_category(name),
            "size": len(data),
            "hash": digest,
            "duplicate": is_dup,
            "duplicate_of": seen_hashes[digest] if is_dup else "",
            "data": data,
        })
    return records


def target_folder(rec, structure: str) -> str:
    cat = rec["category"]
    if structure == "category_ext":
        return f"{cat}/{rec['extension'].lstrip('.').upper() or 'NO_EXT'}"
    if structure == "category_size":
        return f"{cat}/{size_bucket(rec['size'])}"
    return cat


def unique_path(path: str, used: set) -> str:
    if path not in used:
        used.add(path)
        return path
    base, ext = os.path.splitext(path)
    i = 1
    while f"{base}_{i}{ext}" in used:
        i += 1
    new_path = f"{base}_{i}{ext}"
    used.add(new_path)
    return new_path


def build_zip(records, structure, remove_dups, include_report):
    buffer = io.BytesIO()
    used, report_rows = set(), []
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for rec in records:
            if remove_dups and rec["duplicate"]:
                continue
            path = unique_path(f"{target_folder(rec, structure)}/{rec['name']}", used)
            zf.writestr(path, rec["data"])
            report_rows.append({"original_name": rec["original_name"], "saved_as": path,
                                "size": human_size(rec["size"]), "duplicate": rec["duplicate"]})
        if include_report:
            zf.writestr("SORTIFY_Report.csv", pd.DataFrame(report_rows).to_csv(index=False))
    return buffer.getvalue(), len(report_rows)


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=120)
st.sidebar.title("SORTIFY")
menu = st.sidebar.radio("Navigation", ["Home", "Organise Files", "About", "Help"])
st.sidebar.divider()
st.sidebar.caption("Smart file organiser • Made with Streamlit")


# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------
def page_home():
    st.title("📁 Welcome to SORTIFY")
    st.write("Your smart assistant for organising digital files.")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.info("**⚡ Auto Sorting**\n\nFiles are grouped by type instantly.")
    c2.info("**🧹 Duplicate Finder**\n\nSHA-256 hashing finds identical files, even with different names.")
    c3.info("**📦 One-click ZIP**\n\nDownload everything neatly organised with a report.")
    st.write("")
    st.markdown("👉 Sidebar se **Organise Files** select karo aur shuru karo!")


def page_organise():
    st.title("📤 Organise Your Files")

    with st.expander("⚙️ Settings", expanded=True):
        s1, s2 = st.columns(2)
        structure_label = s1.selectbox("Folder structure", list(STRUCTURES.keys()))
        structure = STRUCTURES[structure_label]
        remove_dups = s2.checkbox("Remove duplicate files from ZIP", value=True)
        clean_names = s2.checkbox("Clean file names (spaces → _, lowercase)", value=False)
        include_report = s1.checkbox("Include CSV report inside ZIP", value=True)

    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    if not uploaded_files:
        st.info("Please upload files to start organising!")
        return

    with st.spinner("Analysing files..."):
        records = build_records(uploaded_files, clean_names)

    df = pd.DataFrame([{k: v for k, v in r.items() if k != "data"} for r in records])
    total_size = df["size"].sum()
    dup_count = int(df["duplicate"].sum())
    dup_size = df.loc[df["duplicate"], "size"].sum()

    tab_dash, tab_files, tab_preview, tab_download = st.tabs(
        ["📊 Dashboard", "📂 Files", "🖼️ Preview", "📦 Download"]
    )

    # ---------------- Dashboard ----------------
    with tab_dash:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📁 Total Files", len(records))
        m2.metric("💾 Total Size", human_size(total_size))
        m3.metric("🧬 Duplicates", dup_count)
        m4.metric("♻️ Space Saveable", human_size(dup_size))

        st.divider()
        summary = (df.groupby("category")
                     .agg(files=("name", "count"), size=("size", "sum"))
                     .sort_values("files", ascending=False))

        cols = st.columns(min(len(summary), 4))
        for i, (cat, row) in enumerate(summary.iterrows()):
            cols[i % len(cols)].metric(f"{ICONS.get(cat, '📂')} {cat}", int(row["files"]),
                                       human_size(row["size"]), delta_color="off")

        ch1, ch2 = st.columns(2)
        ch1.subheader("Files per category")
        ch1.bar_chart(summary["files"])
        ch2.subheader("Storage per category (MB)")
        ch2.bar_chart((summary["size"] / MB).round(2))

    # ---------------- Files ----------------
    with tab_files:
        f1, f2 = st.columns([2, 3])
        query = f1.text_input("🔍 Search by name")
        chosen = f2.multiselect("Filter by category", sorted(df["category"].unique()),
                                default=sorted(df["category"].unique()))

        view = df[df["category"].isin(chosen)]
        if query:
            view = view[view["name"].str.contains(query, case=False, na=False)]

        table = view[["name", "category", "extension", "size", "duplicate", "duplicate_of"]].copy()
        table["size"] = table["size"].apply(human_size)
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.subheader("Grouped view")
        for cat, group in view.groupby("category"):
            with st.expander(f"{ICONS.get(cat, '📂')} {cat} ({len(group)} files)"):
                for _, r in group.iterrows():
                    tag = "  🔁 *duplicate*" if r["duplicate"] else ""
                    st.write(f"📄 {r['name']} — `{human_size(r['size'])}`{tag}")

    # ---------------- Preview ----------------
    with tab_preview:
        images = [r for r in records if r["category"] == "Images" and r["extension"] != ".svg"]
        texts = [r for r in records if r["extension"] in (".txt", ".md", ".csv", ".json", ".py")]

        if images:
            st.subheader("Image gallery")
            gcols = st.columns(4)
            for i, rec in enumerate(images[:16]):
                gcols[i % 4].image(rec["data"], caption=rec["name"], use_container_width=True)
            if len(images) > 16:
                st.caption(f"Showing 16 of {len(images)} images.")
        if texts:
            st.subheader("Text preview")
            for rec in texts[:5]:
                with st.expander(rec["name"]):
                    st.code(rec["data"][:2000].decode("utf-8", errors="replace"))
        if not images and not texts:
            st.info("Preview ke liye koi image ya text file nahi mili.")

    # ---------------- Download ----------------
    with tab_download:
        zip_bytes, kept = build_zip(records, structure, remove_dups, include_report)
        st.success(f"ZIP ready: **{kept}** files organised "
                   f"({len(records) - kept} duplicates skipped).")
        stamp = datetime.now().strftime("%Y%m%d_%H%M")

        d1, d2 = st.columns(2)
        d1.download_button("📦 Download Organised ZIP", data=zip_bytes,
                           file_name=f"SORTIFY_Organised_{stamp}.zip",
                           mime="application/zip", use_container_width=True)
        d2.download_button("📝 Download CSV Report",
                           data=df.drop(columns=["hash"]).to_csv(index=False),
                           file_name=f"SORTIFY_Report_{stamp}.csv", mime="text/csv",
                           use_container_width=True)

        st.subheader("Folder structure preview")
        tree = defaultdict(list)
        used = set()
        for rec in records:
            if remove_dups and rec["duplicate"]:
                continue
            path = unique_path(f"{target_folder(rec, structure)}/{rec['name']}", used)
            folder, fname = path.rsplit("/", 1)
            tree[folder].append(fname)
        lines = []
        for folder in sorted(tree):
            lines.append(f"📁 {folder}/")
            lines += [f"   └─ {n}" for n in tree[folder]]
        st.code("\n".join(lines) or "Empty", language=None)


def page_about():
    st.title("ℹ️ About SORTIFY")
    st.write(
        "SORTIFY ek smart file organiser hai jo uploaded files ko type ke hisaab se "
        "sort karta hai, duplicates detect karta hai, aur ek clean ZIP ke roop mein "
        "download karne deta hai."
    )
    st.markdown(
        "- **Frontend & Backend:** Python + Streamlit\n"
        "- **Duplicate detection:** SHA-256 content hashing\n"
        "- **Output:** Organised ZIP + CSV report"
    )


def page_help():
    st.title("❓ Help")
    with st.expander("Files kaise organise karein?", expanded=True):
        st.write("Organise Files page kholo → files upload karo → settings chuno → Download tab se ZIP lo.")
    with st.expander("Duplicate files kaise detect hoti hain?"):
        st.write("File ke content ka hash compare hota hai, naam nahi. Naam alag ho tab bhi duplicate pakda jata hai.")
    with st.expander("Kaunsi file types supported hain?"):
        for cat, exts in FILE_TYPES.items():
            st.write(f"**{ICONS[cat]} {cat}:** {', '.join(exts)}")
        st.write("**📂 Others:** baaki sab kuch.")
    with st.expander("Upload limit kitni hai?"):
        st.write("Default 200MB per file. Badhane ke liye `.streamlit/config.toml` mein "
                 "`[server] maxUploadSize = 1000` set karo.")


{"Home": page_home, "Organise Files": page_organise, "About": page_about, "Help": page_help}[menu]()
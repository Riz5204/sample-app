import os
import pandas as pd
import streamlit as st
from PIL import Image

# データ保存用のCSVファイルと画像用フォルダ
SAVE_FILE = "sample_data.csv"
IMAGE_DIR = "uploaded_images"

# 画像保存用フォルダが無ければ自動作成
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# データの読み込み
if os.path.exists(SAVE_FILE):
    df = pd.read_csv(SAVE_FILE)
else:
    df = pd.DataFrame(
        columns=[
            "サンプル名",
            "保管場所",
            "ボックス・位置",
            "画像パス",
            "登録日時",
        ]
    )

st.title("🧪 超省力 サンプル迷子防止アプリ")

# --- 1. 簡易検索 & 写真閲覧エリア ---
st.subheader("🔍 サンプルを探す")
search_word = st.text_input("サンプル名やキーワードを入力")

# 検索ワードによるデータの絞り込み
if search_word:
    display_df = df[
        df["サンプル名"].str.contains(search_word, case=False, na=False)
    ]
else:
    display_df = df.copy()

# テーブル形式で一覧表示（画像パス列は隠す）
st.dataframe(
    display_df.drop(columns=["画像パス"], errors="ignore"),
    use_container_width=True,
)

# 選択・検索されたサンプルの写真を個別表示
if not display_df.empty:
    st.caption("📷 登録されている写真")
    cols = st.columns(3)  # 3列で写真を並べる
    for idx, (_, row) in enumerate(display_df.iterrows()):
        img_path = row.get("画像パス")
        # 画像が存在する場合に表示
        if pd.notna(img_path) and os.path.exists(img_path):
            with cols[idx % 3]:
                st.image(
                    img_path,
                    caption=f"{row['サンプル名']} ({row['保管場所']})",
                    use_container_width=True,
                )

st.divider()

# --- 2. クイック登録エリア ---
st.subheader("➕ ざっくり新規登録")
col1, col2 = st.columns(2)

with col1:
    sample_name = st.text_input("サンプル名（必須）")
    location = st.selectbox(
        "保管場所",
        [
            "7F 白小冷蔵庫",
            "7F -30℃",
            "7F -80度",
            "7F ピンク冷蔵庫",
        ],
    )

with col2:
    box_info = st.text_input(
        "ボックス名 / 段数", placeholder="例：3段目 赤ボックス A-1"
    )
    photo = st.file_uploader(
        "ボックスの写真をパシャリ (任意)", type=["jpg", "jpeg", "png"]
    )

# 登録ボタンを押したときの処理
if st.button("登録する"):
    if sample_name:
        saved_img_path = ""

        # 画像がアップロードされた場合の保存処理
        if photo is not None:
            # 重複しないファイル名を作成（例: uploaded_images/20260826_サンプル名.jpg）
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(photo.name)[1]
            saved_img_path = os.path.join(
                IMAGE_DIR, f"{timestamp}_{sample_name}{file_ext}"
            )

            # 画像をフォルダへ保存
            image = Image.open(photo)
            image.save(saved_img_path)

        # 新規追加するデータの作成
        new_row = {
            "サンプル名": sample_name,
            "保管場所": location,
            "ボックス・位置": box_info,
            "画像パス": saved_img_path,
            "登録日時": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        }

        # 既存データと結合してCSVへ保存
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(SAVE_FILE, index=False, encoding="utf-8-sig")

        st.success(
            f"「{sample_name}」を【{location} - {box_info}】に保存しました！"
        )
        st.rerun()
    else:
        st.error("サンプル名だけ入力してください！")

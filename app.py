# 以下を「app.py」に書き込み
import spacy
from spacy.pipeline import EntityRuler
from spacy import displacy
import json
import streamlit as st

# Streamlit app title
st.title("エンティティ変換アプリケーション")

# GiNZAモデルの読み込み
nlp = spacy.load("ja_ginza")

# EntityRulerの作成
ruler = nlp.add_pipe("entity_ruler", before="ner")

# 読み込むJSONファイル名のリスト
pattern_files = [
    "ginza_patterns_clinic_matsumoto-oomachi-kiso.json",
    "ginza_patterns_clinic_matsumoto-shi.json",
    "ginza_patterns_hospital.json",
    "ginza_patterns_houkan.json",
    "patterns_trinity_facility.json",
    "patterns_trinity_name.json"
]

# 各ファイルからパターンを読み込む
for file in pattern_files:
    with open(file, encoding="utf-8") as f:
        patterns = json.load(f)
        ruler.add_patterns(patterns)

# テキストを画面から入力する
text = st.text_area("テキストを入力してください（200文字程度表示）:", height=200)

if text:
    # テキストの解析
    doc = nlp(text)

    # 抽出するラベルのリスト
    location_labels = [
        "Country", "City", "Gpe_other", "Occasion_other", "Location",
        "Location_other", "Domestic_region", "Province", "Station",
        "Continental_region", "Theater"
    ]

    facility_labels = [
        "Facility", "Organization", "Company", "School",
        "International_organization", "Goe_other", "Show_organization",
        "Corporation_other"
    ]

    # ラベルを変換した文章を作成する
    modified_text = text
    for ent in doc.ents:
        if ent.label_ in location_labels:
            modified_text = modified_text.replace(ent.text, "[Location]")
        elif ent.label_ in facility_labels:
            modified_text = modified_text.replace(ent.text, "[Facility]")
        elif ent.label_ == "Person":
            modified_text = modified_text.replace(ent.text, "[Person]")

    # 変換後の文章を表示
    st.subheader("変換後の文章")
    st.write(modified_text)

    # 変換後の文章をファイルに書き出す
    with open("output_modified_text.txt", "w", encoding="utf-8") as f:
        f.write(modified_text)

    # displacyで表示する内容をHTMLとして保存（指定されたラベルのみ）
    filtered_ents = []
    for ent in doc.ents:
        if ent.label_ in location_labels:
            ent.label_ = "Location"
            filtered_ents.append(ent)
        elif ent.label_ in facility_labels:
            ent.label_ = "Facility"
            filtered_ents.append(ent)
        elif ent.label_ == "Person":
            filtered_ents.append(ent)

    doc.ents = filtered_ents

    html = displacy.render(doc, style="ent", jupyter=False)

    # HTMLをファイルに書き込む
    with open("output_entities.html", "w", encoding="utf-8") as f:
        f.write(html)

    st.success("エンティティの情報が 'output_entities.html' に保存されました。")
    st.success("変換後の文章が 'output_modified_text.txt' に保存されました。")

# 再度テキスト入力できるようにするためのボタン
if st.button("再度テキストを入力する"):
    st.experimental_rerun()

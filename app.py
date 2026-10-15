import pandas as pd
import streamlit as st

st.title("細菌鑑定工具")
st.info('輸入細菌的形態、革蘭氏染色與各項生化反應結果，系統會與資料庫中的 10 株菌逐一比對，回傳符合的菌種。')
st.markdown("""
1. 依實驗結果，選擇下方 13 項特徵，例如：Shape 選桿菌或球菌，其餘選 +、-、x。
2. 全部選完後，按「開始鑑定」。
3. 若有完全吻合的菌會直接顯示；沒有的話，會列出最接近的菌，並標示差異的項目。
""")
with st.expander("比對規則"):
    st.markdown("""
1. 13 項特徵必須與資料庫完全一致，才算完全吻合。
2. x 代表資料庫中該項為variable reaction，比對時視為一個獨立的值。
3. 沒有完全吻合時，依差異項數由少到多排序，差異數並列的菌會一併顯示。    
""")
with st.expander("資料來源與限制"):
    st.markdown("""
1. 特徵資料整理自教科書
2. 資料庫目前只有 10 株菌；採精確比對，任何一項實驗判讀有誤都會影響結果；結果僅供教學與研究參考。
""")
st.divider()

df = pd.read_csv('bacteria_20250601.csv', encoding='utf-8-sig', dtype=str)
df = df.dropna(how='all')


with st.expander("查看資料庫"):
    st.dataframe(df, hide_index=True)
st.write("共有", len(df), "株菌")

def is_match(row, user_input):
    for key, val in user_input.items():
        if row[key] != val:
            return False
    return True

def find_matches(user_input):
    matches = []
    for i in range(len(df)):
        row = df.iloc[i]              
        if is_match(row, user_input):               
            matches.append(row["Bacteria"])        
    return matches

def get_diffs(row, user_input):
    diffs = []
    for key, val in user_input.items():
        if row[key] != val:
            diffs.append((key, row[key], val))
    return diffs

def find_closest(user_input):
    results = []
    for i in range(len(df)):
        row = df.iloc[i]
        diffs = get_diffs(row, user_input)
        results.append((len(diffs), row["Bacteria"], diffs))
    results.sort()
    return results

features = list(df.columns[1:])
user_input = {}

shape_map = {"1. 桿菌 (Rod)": "1", "2. 球菌 (Cocci)": "2"}

cols = st.columns(3)
for i, f in enumerate(features):
    with cols[i % 3]:                        
        if f == "Shape":                      
            choice = st.selectbox(f, list(shape_map.keys()), index=None, placeholder="請選擇")
            if choice is not None:            
                user_input[f] = shape_map[choice]
        else:                                
            choice = st.selectbox(f, ['+', '-', 'x'], index=None, placeholder="請選擇")                     
            if choice is not None:           
                user_input[f] = choice

st.write("""
1. +: positive
2. -: negative
3. x: variable reaction
""")

if st.button("開始鑑定"):
    st.divider()                      
    if len(user_input) < len(features):       
        st.warning("請選擇所有特徵值")                        
    else:                                      
        result = find_matches(user_input)      
        if len(result) > 0:                    
            st.success(f"找到 {len(result)} 株可能的細菌: {', '.join(result)}")
        else:                                  
            st.warning("未找到符合條件的細菌")
            closest = find_closest(user_input)
            cutoff = closest[2][0]
            for count, name, diffs in closest: 
                if count > cutoff:             
                    break                      
                st.write(f"可能的細菌: {name} (差異數量: {count})")                  
                for key, db_val, in_val in diffs: 
                    if key == "Shape":                
                        db_val = [k for k, v in shape_map.items() if v == db_val][0]  
                        in_val = [k for k, v in shape_map.items() if v == in_val][0]  
                    st.write(f" {key}: 資料庫: '{db_val}', 您輸入: '{in_val}'")             
            st.caption("以上為與您輸入特徵最接近的細菌")                   
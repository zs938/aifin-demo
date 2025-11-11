import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from dotenv import load_dotenv

PORT = int(os.environ.get("PORT", 8501))

# 加载环境变量
load_dotenv()

# 设置页面
st.set_page_config(
    page_title="智囊AIFin - 财务健康分析",
    page_icon="💰",
    layout="wide"
)

# 标题和介绍
st.title("🧠 智囊AIFin - 大学生财务健康分析平台")
st.markdown("""
    上传您的消费记录，AI将为您生成专业的财务健康分析报告！
    *演示版本 - 基于DeepSeek AI驱动*
""")

# 初始化session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# 侧边栏 - 数据输入
with st.sidebar:
    st.header("📊 数据输入")
    
    # 选择数据源
    data_source = st.radio("选择数据来源:", ["使用演示数据", "上传CSV文件"])
    
    if data_source == "使用演示数据":
        df = pd.read_csv('demo_data.csv')
        st.success("已加载演示数据！")
        
    else:  # 上传CSV文件
        uploaded_file = st.file_uploader("上传CSV文件", type=['csv'])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success("文件上传成功！")
        else:
            st.info("请上传CSV文件或使用演示数据")
            st.stop()

# 显示原始数据
st.subheader("原始消费数据")
st.dataframe(df, use_container_width=True)

# 简单的数据统计
col1, col2, col3, col4 = st.columns(4)
total_income = df['收入'].sum()
total_expense = df['支出'].sum()
balance = total_income - total_expense

col1.metric("总收入", f"¥{total_income}")
col2.metric("总支出", f"¥{total_expense}")
col3.metric("结余", f"¥{balance}")
col4.metric("交易笔数", len(df))

# 消费分类饼图
if '分类' in df.columns:
    expense_by_category = df[df['支出'] > 0].groupby('分类')['支出'].sum()
    if not expense_by_category.empty:
        fig = px.pie(
            values=expense_by_category.values, 
            names=expense_by_category.index,
            title="消费分类占比"
        )
        st.plotly_chart(fig, use_container_width=True)

# AI分析按钮
if st.button("🤖 生成AI财务健康报告", type="primary"):
    
    # 准备发送给AI的数据
    financial_data_text = ""
    for _, row in df.iterrows():
        financial_data_text += f"{row['日期']} {row['事项']} 收入:{row['收入']} 支出:{row['支出']} 分类:{row['分类']}\n"
    
    # 构建AI提示词
    prompt = f"""
    你是一名专业的财务顾问，请分析以下大学生的消费记录，生成一份详细且易于理解的财务健康报告。
    
    消费记录：
    {financial_data_text}
    
    请按照以下结构组织你的分析报告：
    
    ## 📈 财务概览
    - 总体收支情况
    - 储蓄率计算
    
    ## 🏷️ 消费结构分析
    - 按类别统计消费占比
    - 指出不合理的消费项目
    
    ## ⚠️ 风险识别
    - 红色警报（严重问题）
    - 黄色预警（需要注意）
    - 绿色亮点（做得好的）
    
    ## 💡 改进建议
    - 具体的、可执行的优化方案
    - 预算分配建议
    
    请用友好的语气，使用emoji让报告更生动，并给出具体的数字和建议。
    """
    
    # 调用DeepSeek API
    with st.spinner('AI正在分析您的财务状况，请稍候...'):
        try:
            api_key = os.getenv('DEEPSEEK_API_KEY')
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers=headers,
                data=json.dumps(data)
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                st.session_state.analysis_result = analysis
            else:
                st.error(f"API调用失败: {response.status_code}")
                
        except Exception as e:
            st.error(f"发生错误: {str(e)}")

# 显示分析结果
if st.session_state.analysis_result:
    st.subheader("📋 AI财务健康分析报告")
    st.markdown(st.session_state.analysis_result)
    
    # 添加下载按钮
    st.download_button(
        label="下载分析报告",
        data=st.session_state.analysis_result,
        file_name="财务健康分析报告.md",
        mime="text/markdown"
    )

# 功能说明
with st.expander("ℹ️ 关于此演示"):
    st.markdown("""
    **这是一个概念验证演示，展示了智囊AIFin的核心能力：**
    
    - ✅ **自动消费分类与分析**
    - ✅ **AI驱动的财务健康评估**
    - ✅ **个性化改进建议生成**
    - ✅ **可视化数据展示**
    
    **在实际产品中，我们将：**
    - 直接对接银行API，实现无感数据同步
    - 构建更专业的金融知识库
    - 实现更精准的消费预测和规划

    """)

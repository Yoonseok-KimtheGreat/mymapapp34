import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="글로벌 주요 기업 주가 분석",
    page_icon="📈",
    layout="wide"
)

# 시총 Top 10 기업 (2024년 기준)
TOP_10_COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT", 
    "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
    "Meta (Facebook)": "META",
    "Berkshire Hathaway": "BRK-B",
    "Taiwan Semiconductor": "TSM",
    "Visa": "V"
}

# 차세대 AI 주요 기업
AI_COMPANIES = {
    "NVIDIA": "NVDA",                     # AI 반도체
    "AMD": "AMD",                         # AI GPU 경쟁자
    "Palantir": "PLTR",                   # AI 기반 빅데이터 분석
    "Snowflake": "SNOW",                 # 데이터 인프라
    "ServiceNow": "NOW",                  # AI 자동화 SaaS
    "UiPath": "PATH",                     # RPA + AI
    "C3.ai": "AI",                        # 엔터프라이즈 AI
    "SoundHound AI": "SOUN",             # 음성 인식 AI
    "Arm Holdings": "ARM",               # AI 칩 설계
    "Symbotic": "SYM"                     # AI 기반 물류 자동화
}

# 선택 가능한 유형
COMPANY_GROUPS = {
    "시총 Top 10 기업": TOP_10_COMPANIES,
    "차세대 AI 주요 기업": AI_COMPANIES
}

@st.cache_data
def get_stock_data(ticker, period="3y"):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        return data
    except Exception as e:
        st.error(f"{ticker} 데이터를 가져오는 중 오류 발생: {e}")
        return None

@st.cache_data
def get_company_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'marketCap': info.get('marketCap', 0),
            'currentPrice': info.get('currentPrice', 0)
        }
    except:
        return {'name': 'N/A', 'sector': 'N/A', 'marketCap': 0, 'currentPrice': 0}

def format_market_cap(market_cap):
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def main():
    st.title("📈 글로벌 주요 기업 주가 분석")
    st.markdown("시총 상위 기업과 차세대 AI 기업들의 최근 주가 흐름을 비교해보세요.")
    
    # 기업 유형 선택
    company_group = st.sidebar.radio("기업 그룹 선택", list(COMPANY_GROUPS.keys()))
    companies_dict = COMPANY_GROUPS[company_group]
    
    selected_companies = st.sidebar.multiselect(
        "분석할 기업을 선택하세요:",
        options=list(companies_dict.keys()),
        default=list(companies_dict.keys())[:3]
    )
    
    if not selected_companies:
        st.warning("최소 하나의 기업을 선택해주세요.")
        return

    # 기간 선택
    period_options = {"1년": "1y", "2년": "2y", "3년": "3y", "5년": "5y"}
    selected_period = st.sidebar.selectbox("기간 선택:", list(period_options.keys()), index=2)

    # 차트 타입
    chart_type = st.sidebar.radio("차트 타입:", ["라인 차트", "캔들스틱 차트"])
    
    # 데이터 불러오기
    with st.spinner("데이터를 불러오는 중..."):
        stock_data = {}
        company_info = {}
        for company in selected_companies:
            ticker = companies_dict[company]
            data = get_stock_data(ticker, period_options[selected_period])
            info = get_company_info(ticker)
            if data is not None and not data.empty:
                stock_data[company] = data
                company_info[company] = info
    
    if not stock_data:
        st.error("데이터를 불러올 수 없습니다.")
        return
    
    # 기업 정보 출력
    st.header("📊 선택된 기업 정보")
    cols = st.columns(len(selected_companies))
    for i, company in enumerate(selected_companies):
        info = company_info[company]
        with cols[i]:
            st.metric(
                label=f"{company}",
                value=f"${info['currentPrice']:.2f}",
                delta=f"시총: {format_market_cap(info['marketCap'])}"
            )
            st.caption(f"섹터: {info['sector']}")

    # 주가 차트
    st.header("📈 주가 차트")
    if chart_type == "라인 차트":
        fig = go.Figure()
        colors = px.colors.qualitative.Set1 * 2
        for i, (company, data) in enumerate(stock_data.items()):
            fig.add_trace(go.Scatter(
                x=data.index, y=data['Close'], name=company,
                mode='lines', line=dict(color=colors[i]),
                hovertemplate=f"<b>{company}</b><br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>"
            ))
        fig.update_layout(
            title=f"주가 추이 - {selected_period}",
            xaxis_title="날짜", yaxis_title="주가 (USD)",
            hovermode='x unified', height=600, template='plotly_white'
        )
    else:
        company = selected_companies[0]
        data = stock_data[company]
        fig = go.Figure(data=go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name=company
        ))
        fig.update_layout(
            title=f"{company} 캔들스틱 차트 - {selected_period}",
            xaxis_title="날짜", yaxis_title="주가 (USD)",
            height=600, template='plotly_white'
        )
        if len(selected_companies) > 1:
            st.info("캔들스틱 차트는 하나의 기업만 지원됩니다.")

    st.plotly_chart(fig, use_container_width=True)

    # 성과 비교
    st.header("📊 성과 비교")
    performance_data = []
    for company, data in stock_data.items():
        start = data['Close'].iloc[0]
        end = data['Close'].iloc[-1]
        change = ((end - start) / start) * 100
        performance_data.append({
            '기업': company,
            '시작 가격': f"${start:.2f}",
            '현재 가격': f"${end:.2f}",
            '총 수익률': f"{change:.2f}%",
            '최고가': f"${data['Close'].max():.2f}",
            '최저가': f"${data['Close'].min():.2f}",
            '변동성': f"{data['Close'].std():.2f}"
        })
    st.dataframe(pd.DataFrame(performance_data), use_container_width=True)

    # 거래량 차트
    st.header("📊 거래량 분석")
    fig_volume = go.Figure()
    for i, (company, data) in enumerate(stock_data.items()):
        fig_volume.add_trace(go.Scatter(
            x=data.index, y=data['Volume'], name=company,
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f"<b>{company}</b><br>Date: %{{x}}<br>Volume: %{{y:,}}<extra></extra>"
        ))
    fig_volume.update_layout(
        title=f"거래량 추이 - {selected_period}",
        xaxis_title="날짜", yaxis_title="거래량",
        hovermode='x unified', height=400, template='plotly_white'
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    # 주의사항
    st.header("ℹ️ 추가 정보")
    st.info("""
    **데이터 소스**: Yahoo Finance

    **면책 조항**: 
    - 본 데이터는 투자 조언이 아닙니다.
    - 실제 투자 전에 전문가와 상담하세요.
    - 과거의 수익률은 미래의 수익을 보장하지 않습니다.
    """)

if __name__ == "__main__":
    main()

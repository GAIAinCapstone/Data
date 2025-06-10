# Data

자 보니까... 보령/신보령/신서천 18-25년까지, TSP, SOx, NOx, O₂, FL1 데이터가 있슴다
산소 이상치 반영하고 비는값은 대충 채워서 전처리해뒀고 prepro보면 알겠지만 각 발전소별/물질별/연도별로 csv파일 만들어둔상태임 그리고 이거 데베에 올림(또는 올릴예정)
기상 데이터 어케 전처리해야할지는 수민이랑 찬민이랑 회의해봐야할거같고 어케든 일단 은송언니가 만든 웹페이지에 데이터 연동돼서 트랜스포머 모델 학습시키고, 그래프만 나오면 되는거자네?
그래서 데베에 올린 데이터 형태 잘 들어갈 수 있도록 streamlit페이지를 수정해야겠다 들었음
남은시간 파이팅하자구

**보령 오염물질 데이터(TSP, SOx, NOx)**

https://docs.google.com/spreadsheets/d/1LJufS1W2n6CO1ZER1YvS-Bv2kzuJm3EZ/edit?usp=drive_link&ouid=110290650670943010674&rtpof=true&sd=true

**보령 추가 데이터(O₂, FL1)**

https://docs.google.com/spreadsheets/d/19mBZVN-bWFMXqWwy_2IlZ9GAQhEYz7Fm/edit?usp=drive_link&ouid=110290650670943010674&rtpof=true&sd=true

**보령 오염물질 데이터(TSP, SOx, NOx) json 파일형식**

https://drive.google.com/file/d/1q4JDdu6nBakKN1Uci9QEMmIRiJI1iebR/view?usp=sharing

FROM python:3.8
ENV PATH /usr/local/bin:$PATH
ADD . /qq_bot
WORKDIR /qq_bot
RUN pip install -r requirements.txt
RUN pip install nonebot-adapter-cqhttp
CMD python3 bot.py
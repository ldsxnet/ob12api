FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 备份默认配置到独立目录，挂载空卷覆盖 /app/config 后应用会自动恢复
RUN mkdir -p /app/config.default && cp /app/config/setting.toml /app/config.default/

EXPOSE 8081

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8081"]

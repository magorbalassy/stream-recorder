FROM  nginx:1.24.0
LABEL maintainer="Magor Balassy"

USER root

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN echo 'alias ll="ls -l"' >> ~/.bashrc

# Set work directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
RUN mkdir -p /app/frontend/assets
COPY backend/frontend/* /app/frontend/
COPY backend/frontend/assets/* /app/frontend/assets
COPY backend/app.py /app/
COPY backend/requirements.txt /app/
COPY backend/appentry.sh /app/
RUN chmod +x /app/appentry.sh
RUN sed -i '$d' /docker-entrypoint.sh
RUN echo "/app/appentry.sh" >> /docker-entrypoint.sh
RUN echo 'exec "$@"' >>  /docker-entrypoint.sh


RUN pip install -r requirements.txt

# Configure image with the app user and correct permissions
# RUN groupadd appuser -f -g 1002 && \
#     adduser -u 1002 --ingroup appuser appuser && \
#     chown -R appuser:appuser /app && \
#     chmod -R 755 /app

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/server.conf


# User who will be running the application
# USER appuser

# Entrypoint specifies default command to execute when the image runs
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 80

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]

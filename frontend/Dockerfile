FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/
COPY menu-data.json /usr/share/nginx/html/

# Create directory for assets
RUN mkdir -p /usr/share/nginx/html/assets

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
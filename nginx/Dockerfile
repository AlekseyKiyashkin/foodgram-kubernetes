FROM kryssperer/foodgram-frontend:2.8 as build


FROM nginx:1.19.3
RUN pwd
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html/
COPY docs/ /usr/share/nginx/html/api/
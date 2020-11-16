FROM nathangeology/lambda-deploy-env
ARG package_name
ARG bucket_name
ARG zip_file_name
ARG layer_name
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
RUN mkdir pkg_build
WORKDIR /srv/pkg_build
RUN python3 -m venv temp_env
RUN source ./temp_env/bin/activate
RUN mkdir python
COPY . ./$package_name/
RUN python3 -m pip install ./$package_name/ --target ./python
RUN zip -r9 f.zip ./python
RUN aws s3 cp f.zip s3://$bucket_name/$zip_file_name
RUN aws lambda publish-layer-version \
    --layer-name $layer_name \
    --description "Base Data Access Layer lambda library" \
    --license-info "MIT" \
    --content S3Bucket=$bucket_name,S3Key=$zip_file_name \
    --compatible-runtimes python3.7 python3.8
RUN echo DONE
CMD ["/bin/bash"]

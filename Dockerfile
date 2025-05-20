FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies including compression and build tools
RUN yum update -y && \
    yum install -y \
    wget \
    make \
    gcc \
    gcc-c++ \
    automake \
    autoconf \
    libtool \
    pkgconfig \
    libjpeg-devel \
    libpng-devel \
    libtiff-devel \
    zlib-devel \
    gzip \
    tar \
    git \
    poppler \
    poppler-utils \
    poppler-devel \
    && yum clean all

# Install additional build dependencies
RUN yum install -y \
    cairo-devel \
    pango-devel \
    icu libicu-devel \
    && yum clean all

# Set environment variables for build
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install Leptonica from source
RUN wget http://www.leptonica.org/source/leptonica-1.82.0.tar.gz && \
    tar -zxvf leptonica-1.82.0.tar.gz && \
    cd leptonica-1.82.0 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf leptonica-1.82.0*

# Install Tesseract from source
RUN wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.3.3.tar.gz && \
    tar -zxvf 5.3.3.tar.gz && \
    cd tesseract-5.3.3 && \
    ./autogen.sh && \
    PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
    ./configure --prefix=/usr/local \
    --with-extra-includes=/usr/local/include \
    --with-extra-libraries=/usr/local/lib && \
    make && \
    make install && \
    cd .. && \
    rm -rf 5.3.3.tar.gz tesseract-5.3.3

# Install English language data
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    mkdir -p /usr/local/share/tessdata && \
    mv eng.traineddata /usr/local/share/tessdata/

# Set environment variables
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install -r requirements.txt

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "lambda_handler.handler" ]
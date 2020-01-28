FROM alpine:3.9

# python3 and node.js with yarn
RUN apk add --no-cache python3 yarn && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache


# numpy, scipy, matplotlib
RUN apk add --no-cache \
        --virtual=.build-dependencies \
        g++ gfortran file binutils \
        musl-dev python3-dev openblas-dev && \
    apk add libstdc++ openblas && \
    apk add --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
            --update --no-cache libgfortran && \
    apk add --update --no-cache build-base \
                                libpng libpng-dev \
                                freetype freetype-dev && \
    \
    ln -s locale.h /usr/include/xlocale.h && \
    \
    pip3 install numpy && \
    pip3 install matplotlib && \
    pip3 install scipy && \
    \
    rm -r /root/.cache && \
    find /usr/lib/python3.*/ -name 'tests' -exec rm -r '{}' + && \
    find /usr/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; && \
    \
    rm /usr/include/xlocale.h && \
    \
    apk del .build-dependencies && \
    apk del --purge build-base libgfortran libpng-dev freetype-dev \
                    py-numpy-dev && \
    rm -vrf /var/cache/apk/*


# ngspice
RUN apk add --no-cache --virtual=.build-dependencies \
    autoconf \
    automake \
    bison \
    curl \
    flex \
    g++ \
    libtool \
    make \
    ncurses-dev \
    readline-dev && \
    apk add libx11-dev libxaw-dev libgomp && \
    curl -fSL https://github.com/imr/ngspice/archive/ngspice-30.tar.gz -o ngspice.tar.gz \
    && mkdir -p /usr/src \
    && tar -zxC /usr/src -f ngspice.tar.gz \
    && rm ngspice.tar.gz \
    && cd /usr/src/ngspice-ngspice-30 \
    && ./autogen.sh \
    && ./configure --enable-xspice --disable-debug --enable-cider --with-readline=yes --enable-openmp --with-ngshared \
    && make \
    && make install && \
    apk del .build-dependencies && \ 
    rm -vrf /var/cache/apk/* 

# schema-vc
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN apk add --no-cache \
        --virtual=.build-dependencies \
        gcc g++ git python3-dev python-dev musl-dev libffi-dev && \
    pip3 install --no-deps git+https://github.com/xesscorp/skidl && \
    pip3 install -r /app/requirements.txt && \
    apk del .build-dependencies && \ 
    rm -vrf /var/cache/apk/*

RUN sed -i -e 's/latin_1/utf8/g' /usr/lib/python3.6/site-packages/skidl/utilities.py
RUN sed -i -e 's/(value {value})/(value "{value}")/g' /usr/lib/python3.6/site-packages/skidl/utilities.py

ADD ./bem /app/bem
ADD ./blocks /app/blocks
ADD ./spice /app/spice
ADD ./probe /app/probe
ADD ./settings.py /app/settings.py
ADD ./api.py /app/api.py
COPY ./data.db /app/data.db
ADD ./kicad /app/kicad/

RUN cd bem && yarn install 

ENTRYPOINT [ "python3" ]
CMD ["api.py"]

FROM nanguage/pantheon-agents:latest

# Upgrade R to 4.5.x from CRAN
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends dirmngr gnupg apt-transport-https && \
    gpg --keyserver keyserver.ubuntu.com --recv-key '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' && \
    gpg --armor --export '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' | tee /etc/apt/trusted.gpg.d/cran_debian_key.asc && \
    echo 'deb https://cloud.r-project.org/bin/linux/debian bookworm-cran40/' > /etc/apt/sources.list.d/cran.list && \
    apt-get update -qq && \
    apt-get install -y r-base r-base-dev && \
    rm -rf /var/lib/apt/lists/*

# System libraries needed by common R packages
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    libuv1-dev libcurl4-openssl-dev libssl-dev libxml2-dev \
    libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
    libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev \
    libhdf5-dev libgsl-dev \
    && rm -rf /var/lib/apt/lists/*

# Re-install IRkernel for upgraded R 4.5.x (base image has it for stock R)
RUN R -e "install.packages('IRkernel', repos='https://cloud.r-project.org', Ncpus=parallel::detectCores())" && \
    R -e "IRkernel::installspec(user = FALSE)"

FROM jupyter/base-notebook:5811dcb711ba

USER root

RUN apt-get update \
  && apt-get install -yq gpg

RUN echo "deb http://packages.cloud.google.com/apt cloud-sdk-xenial main" > /etc/apt/sources.list.d/google-cloud-sdk.list

RUN wget https://packages.cloud.google.com/apt/doc/apt-key.gpg -q -O - | sudo apt-key add -

RUN apt-get update \
  && apt-get install -yq --no-install-recommends \
        vim git jq less openssh-client google-cloud-sdk \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER $NB_USER

RUN conda update -n base conda
RUN conda config --add channels conda-forge --force
RUN conda install --yes  \
    av>=0.4.0 \
    bokeh=0.12.16 \
    cython \
    cytoolz \
    dask \
    dask-kubernetes \
    distributed \
    google-cloud-storage \
    imagehash \
    ipywidgets \
    julia \
    lz4 \
    matplotlib \
    nbserverproxy \
    netcdf4 \
    nomkl \
    numba \
    numcodecs \
    numpy \
    pandas \
    pytables \
    python-blosc \
    scipy \
    scikit-image \
    xarray \
    zict \
    && conda clean -tipsy

RUN pip install --upgrade pip
RUN pip install numpngw \
                azure-storage-blob
RUN pip install git+https://github.com/tjcrone/pycamhd@8bdc18647ec20b0a49dc140d3f71b8ef9dba17a9
RUN pip install git+https://github.com/tjcrone/flowmow

RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager

USER root
COPY prepare.sh /usr/bin/prepare.sh
RUN chmod +x /usr/bin/prepare.sh

RUN mkdir /pre-home && chown -R $NB_USER /pre-home
COPY config.yaml /pre-home
COPY worker-template.yaml /pre-home

# fix .ssh permissions
RUN printf "\n#fix .ssh permissions\nif [ -f /home/$NB_USER/.ssh/id_rsa ]; then\n   chmod 400 \"/home/$NB_USER/.ssh/id_rsa\"\nfi\nif [ -f /home/$NB_USER/.ssh/id_rsa.pub ]; then\n   chmod 444 \"/home/$NB_USER/.ssh/id_rsa.pub\"\nfi\nif [ -f /home/$NB_USER/.ssh/known_hosts ]; then\n   chmod 600 \"/home/$NB_USER/.ssh/known_hosts\"\nfi\n" >> /etc/bash.bashrc

# Add NB_USER to sudo
RUN echo "$NB_USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/notebook
RUN sed -ri "s#Defaults\s+secure_path=\"([^\"]+)\"#Defaults secure_path=\"\1:$CONDA_DIR/bin\"#" /etc/sudoers
USER $NB_USER

ENTRYPOINT ["tini", "--", "/usr/bin/prepare.sh"]
CMD ["start.sh jupyter lab"]

FROM python:3

RUN useradd -ms /bin/bash myuser
USER myuser

WORKDIR /home/myuser/code
COPY --chown=myuser:myuser requirements.txt /home/myuser/code/

ENV PATH="/home/myuser/.local/bin:${PATH}"

RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

COPY --chown=myuser:myuser . /home/myuser/code/
# Saligiare Sandbox 镜像

这个镜像是 Phase 4 的最小执行环境：非 root 用户、默认由 `DockerSandbox` 关闭网络，并把任务工作目录挂载到 `/workspace`。

在 Docker daemon 可用的机器上构建：

```bash
docker build -t saligiare-sandbox:test -f docker/sandbox/Dockerfile .
```

构建后运行可选 smoke test：

```bash
SALIGIARE_DOCKER_SMOKE=1 \
SALIGIARE_SANDBOX_IMAGE=saligiare-sandbox:test \
python -m pytest tests/sandbox/test_docker_smoke.py -q
```

测试只运行 Alpine 镜像内置的 `/bin/busybox printf`，不访问公共网络，不执行仓库中的安全项目代码。

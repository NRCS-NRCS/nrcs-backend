from apps.common.github import DeploymentStatusEnum, derive_status, has_active_run


class TestDeriveStatus:
    def test_in_progress(self):
        assert derive_status({"status": "in_progress", "conclusion": None}) == DeploymentStatusEnum.IN_PROGRESS

    def test_queued_variants(self):
        for status in ("queued", "waiting", "pending", "requested"):
            assert derive_status({"status": status, "conclusion": None}) == DeploymentStatusEnum.QUEUED, status

    def test_completed_conclusions(self):
        cases = {
            "success": DeploymentStatusEnum.SUCCESS,
            "neutral": DeploymentStatusEnum.SUCCESS,
            "failure": DeploymentStatusEnum.FAILED,
            "timed_out": DeploymentStatusEnum.FAILED,
            "startup_failure": DeploymentStatusEnum.FAILED,
            "action_required": DeploymentStatusEnum.FAILED,
            "cancelled": DeploymentStatusEnum.CANCELLED,
            "skipped": DeploymentStatusEnum.CANCELLED,
            "stale": DeploymentStatusEnum.CANCELLED,
        }
        for conclusion, expected in cases.items():
            assert derive_status({"status": "completed", "conclusion": conclusion}) == expected, conclusion

    def test_unknown_values_do_not_raise(self):
        # A status or conclusion GitHub adds later must degrade to UNKNOWN, never blow up
        # the whole deployments query.
        assert derive_status({"status": "completed", "conclusion": "brand_new"}) == DeploymentStatusEnum.UNKNOWN
        assert derive_status({"status": "completed", "conclusion": None}) == DeploymentStatusEnum.UNKNOWN
        assert derive_status({"status": "brand_new", "conclusion": None}) == DeploymentStatusEnum.UNKNOWN
        assert derive_status({}) == DeploymentStatusEnum.UNKNOWN


class TestHasActiveRun:
    def test_empty(self):
        assert has_active_run([]) is False

    def test_all_completed(self):
        assert has_active_run([{"status": "completed"}, {"status": "completed"}]) is False

    def test_one_active(self):
        assert has_active_run([{"status": "completed"}, {"status": "in_progress"}]) is True
        assert has_active_run([{"status": "queued"}]) is True

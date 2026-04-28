from __future__ import annotations

from app.services.workspace_audit import diff_workspace, snapshot_workspace


def test_workspace_diff_reports_added_modified_and_removed_files(tmp_path) -> None:
    hdl_dir = tmp_path / "hdl"
    hdl_dir.mkdir()
    dut_path = hdl_dir / "dut.v"
    removed_path = hdl_dir / "old.v"
    dut_path.write_text("module dut; endmodule", encoding="utf-8")
    removed_path.write_text("old", encoding="utf-8")
    before = snapshot_workspace(tmp_path)

    dut_path.write_text("module dut; wire fixed; endmodule", encoding="utf-8")
    removed_path.unlink()
    (hdl_dir / "new.v").write_text("new", encoding="utf-8")
    after = snapshot_workspace(tmp_path)

    assert diff_workspace(before, after) == ["hdl/dut.v", "hdl/new.v", "hdl/old.v"]


def test_workspace_diff_reports_no_changes(tmp_path) -> None:
    (tmp_path / "dut.v").write_text("module dut; endmodule", encoding="utf-8")
    before = snapshot_workspace(tmp_path)

    assert diff_workspace(before, snapshot_workspace(tmp_path)) == []

WITH usage_month AS (
    SELECT * FROM {{ ref('pings_usage_data_month') }}
)


SELECT
     DISTINCT *,
     (auto_devops_disabled > 0)::int                   AS auto_devops_disabled_active,
     (auto_devops_enabled > 0)::int                    AS auto_devops_enabled_active,
     (boards > 0)::int                                 AS boards_active,
     (ci_builds > 0)::int                              AS ci_builds_active,
     (ci_external_pipelines > 0)::int                  AS ci_external_pipelines_active,
     (ci_internal_pipelines > 0)::int                  AS ci_internal_pipelines_active,
     (ci_pipeline_config_auto_devops > 0)::int         AS ci_pipeline_config_auto_devops_active,
     (ci_pipeline_config_repository > 0)::int          AS ci_pipeline_config_repository_active,
     (ci_pipeline_schedules > 0)::int                  AS ci_pipeline_schedules_active,
     (ci_runners > 0)::int                             AS ci_runners_active,
     (ci_triggers > 0)::int                            AS ci_triggers_active,
     (clusters > 0)::int                               AS clusters_active,
     (clusters_applications_helm > 0)::int             AS clusters_applications_helm_active,
     (clusters_applications_ingress > 0)::int          AS clusters_applications_ingress_active,
     (clusters_applications_prometheus > 0)::int       AS clusters_applications_prometheus_active,
     (clusters_applications_runner > 0)::int           AS clusters_applications_runner_active,
     (clusters_disabled > 0)::int                      AS clusters_disabled_active,
     (clusters_enabled > 0)::int                       AS clusters_enabled_active,
     (clusters_platforms_gke > 0)::int                 AS clusters_platforms_gke_active,
     (clusters_platforms_user > 0)::int                AS clusters_platforms_user_active,
     (deploy_keys > 0)::int                            AS deploy_keys_active,
     (deployments > 0)::int                            AS deployments_active,
     (environments > 0)::int                           AS environments_active,
     (gcp_clusters > 0)::int                           AS gcp_clusters_active,
     (groups > 0)::int                                 AS groups_active,
     (in_review_folder > 0)::int                       AS in_review_folder_active,
     (issues > 0)::int                                 AS issues_active,
     (keys > 0)::int                                   AS keys_active,
     (labels > 0)::int                                 AS labels_active,
     (lfs_objects > 0)::int                            AS lfs_objects_active,
     (merge_requests > 0)::int                         AS merge_requests_active,
     (milestones > 0)::int                             AS milestones_active,
     (notes > 0)::int                                  AS notes_active,
     (pages_domains > 0)::int                          AS pages_domains_active,
     (projects_prometheus_active > 0)::int             AS projects_prometheus_active_active,
     (projects > 0)::int                               AS projects_active,
     (projects_imported_from_github > 0)::int          AS projects_imported_from_github_active,
     (protected_branches > 0)::int                     AS protected_branches_active,
     (releases > 0)::int                               AS releases_active,
     (remote_mirrors > 0)::int                         AS remote_mirrors_active,
     (snippets > 0)::int                               AS snippets_active,
     (todos > 0)::int                                  AS todos_active,
     (uploads > 0)::int                                AS uploads_active,
     (web_hooks > 0)::int                              AS web_hook_actives
FROM usage_month
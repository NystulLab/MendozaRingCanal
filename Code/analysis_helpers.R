read_analysis_csv <- function(path) {
  readr::read_csv(path, show_col_types = FALSE)
}

summarize_mean_sd <- function(data, group_cols, value_col) {
  data %>%
    group_by(across(all_of(group_cols))) %>%
    summarise(
      Mean = mean({{ value_col }}, na.rm = TRUE),
      SD = sd({{ value_col }}, na.rm = TRUE),
      n = sum(!is.na({{ value_col }})),
      .groups = "drop"
    )
}

manuscript_theme <- function(base_size = 8, base_family = "Arial") {
  ggprism::theme_prism(base_size = base_size, base_family = base_family) +
    theme(
      text = element_text(family = base_family, size = base_size),
      axis.text = element_text(family = base_family, size = base_size),
      axis.title = element_text(family = base_family, size = base_size),
      plot.title = element_text(family = base_family, size = base_size, hjust = 0.5),
      legend.title = element_text(family = base_family, size = base_size),
      legend.text = element_text(family = base_family, size = base_size),
      strip.text = element_text(family = base_family, size = base_size)
    )
}

plot_box_jitter <- function(data, summary_data = data, x, y, plot_title,
                            title_size = 10,
                            y_label = NULL,
                            x_label = NULL,
                            y_limits = NULL, y_labels = waiver(),
                            p_values = NULL, x_labels = waiver(),
                            box_fill = "grey85", jitter_width = 0.2,
                            point_size = 1.2, bracket_size = 0.3,
                            p_value_size = 2.5, box_linewidth = 0.35,
                            base_size = 8, base_family = "Arial") {
  plot <- ggplot() +
    geom_boxplot(
      data = summary_data,
      aes(x = {{ x }}, y = {{ y }}),
      fill = box_fill,
      linewidth = box_linewidth,
      outlier.shape = NA
    ) +
    geom_jitter(
      data = data,
      aes(x = {{ x }}, y = {{ y }}, colour = as.factor(Replicate)),
      width = jitter_width,
      height = 0,
      size = point_size,
      alpha = 0.8
    ) +
    scale_color_brewer(palette = "Dark2") +
    scale_x_discrete(labels = x_labels) +
    scale_y_continuous(labels = y_labels, limits = y_limits) +
    manuscript_theme(base_size = base_size, base_family = base_family) +
    labs(x = x_label, y = y_label, title = plot_title) +
    theme(
      legend.position = "none",
      plot.title = element_text(size = title_size))

  if (!is.null(p_values)) {
    plot <- plot +
      ggpubr::stat_pvalue_manual(
        p_values,
        label = "p.signif",
        tip.length = 0.05,
        bracket.size = bracket_size,
        size = p_value_size,
        family = base_family,
        hide.ns = TRUE
      )
  }

  plot
}

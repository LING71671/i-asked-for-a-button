# 视觉作品的配色

[English](color.md)

　　选择或修改配色时读取本参考，结合读者、内容、环境和预期气质，优先沿用合适的已有设计系统。局部改动检查受影响的颜色组合和状态即可。

## 色彩关系与层次

　　有意识地选择配色关系：单色使用同一色相的明暗变化；类似色使用相邻色相；互补色使用色环相对的色相；分裂互补使用互补色两侧的色相；三角配色使用等距的三个色相。再通过明度、彩度和使用面积安排主次，让中性表面承载内容、强调色服务重点。各区域不必同样抢眼，也不统一套用一种配色或固定面积比例。[Adobe 配色关系](https://www.adobe.com/uk/creativecloud/design/discover/color-palette.html)。

## 颜色角色与状态

　　为背景、内容层、文字、必要控件边界、操作、选中、焦点和状态分配可复用角色，区分装饰分隔线和辨认控件所需的边界。文字与实际背景成对选择，在控件、展开菜单及悬停、按下、选中、禁用和错误状态中保持含义一致。深色和局部反差区域分别设计颜色组合。[Material 颜色角色](https://m3.material.io/styles/color/the-color-system)、[Fluent 配色](https://fluent2.microsoft.design/color)。

　　有需要时，表格交替底色可辅助追踪行，但仍须保证内容可读、选中状态明确。交替底色、互补色、局部反差区域和像素反色属于不同选择，深色主题应按角色配色。[MDN 反色说明](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/filter-function/invert)。

## 可见性与舒适性

　　WCAG AA 要求普通文字与背景至少 4.5:1、大号文字至少 3:1；必要的非文字控件或状态线索与相邻颜色至少 3:1，禁用控件有例外。装饰边界、悬停与默认状态之间的差别并非一律要求 3:1。结合透明度和覆盖层检查实际颜色，不能把未达标比值四舍五入为通过。颜色承担含义时，还应有勾选、形状、标签等可见区别。[文字对比](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)、[非文字对比](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)、[颜色的使用](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)。

　　在目标尺寸和主题下查看实际画面，检查字号、字重、行长行距、内容密度、争抢注意力的强调色、大面积高亮或高彩度区域，以及焦点和选中状态。缓和刺眼感时仍须保持重要文字清楚，尊重可用的字号、对比和主题偏好。WCAG 视觉呈现指南另有 AAA 条款，按具体要求采用。分别观察可见性、审美契合度和阅读舒适性，报告实际检查的颜色、状态、尺寸和结果。[视觉呈现](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html)。

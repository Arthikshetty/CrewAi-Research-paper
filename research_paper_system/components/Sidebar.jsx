import React, { useState } from "react";
import {
  LayoutDashboard,
  Search,
  Award,
  Users,
  BarChart3,
  Network,
  FileText,
  Lightbulb,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";

/* ---------------- Menu Data ---------------- */
const MENU_SECTIONS = [
  {
    header: "Main",
    items: [
      { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
      { id: "search", label: "Search", icon: Search },
      { id: "best-papers", label: "Best Papers", icon: Award },
    ],
  },
  {
    header: "Analytics",
    items: [
      { id: "top-authors", label: "Top Authors", icon: Users },
      { id: "rankings", label: "Rankings", icon: BarChart3 },
      { id: "citation-graph", label: "Citation Graph", icon: Network },
    ],
  },
  {
    header: "Content",
    items: [
      { id: "summaries", label: "Summaries", icon: FileText },
      { id: "ideas", label: "Ideas", icon: Lightbulb },
      { id: "problem-statements", label: "Problem Statements", icon: AlertCircle },
    ],
  },
];

/* ---------------- Menu Item ---------------- */
function MenuItem({ item, active, collapsed, onClick }) {
  const Icon = item.icon;
  const isActive = active === item.id;

  return (
    <li className="relative group">
      <button
        onClick={() => onClick(item.id)}
        aria-label={item.label}
        aria-current={isActive ? "page" : undefined}
        className={[
          "relative flex items-center w-full rounded-xl transition-all duration-300 ease-in-out",
          collapsed ? "justify-center px-2 py-3" : "px-3 py-2.5 gap-3",
          isActive
            ? "bg-gradient-to-r from-violet-500/25 via-fuchsia-500/15 to-transparent text-white font-semibold shadow-[0_0_20px_rgba(168,85,247,0.25)]"
            : "text-slate-300 hover:text-white hover:bg-white/5 hover:scale-[1.03]",
        ].join(" ")}
      >
        {/* Active left indicator */}
        {isActive && (
          <span
            className="absolute left-0 top-1/2 -translate-y-1/2 h-7 w-1 rounded-r-full bg-gradient-to-b from-fuchsia-400 to-violet-500 shadow-[0_0_10px_rgba(217,70,239,0.8)]"
            aria-hidden="true"
          />
        )}

        <Icon
          className={[
            "flex-shrink-0 transition-transform duration-300",
            collapsed ? "h-5 w-5" : "h-[18px] w-[18px]",
            isActive ? "text-fuchsia-300" : "text-slate-400 group-hover:text-violet-300",
          ].join(" ")}
        />

        {!collapsed && (
          <span className="text-sm tracking-wide truncate">{item.label}</span>
        )}
      </button>

      {/* Tooltip when collapsed */}
      {collapsed && (
        <span
          role="tooltip"
          className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-3 z-50
                     whitespace-nowrap rounded-md bg-slate-900/95 backdrop-blur px-2.5 py-1.5
                     text-xs font-medium text-white shadow-lg ring-1 ring-white/10
                     opacity-0 group-hover:opacity-100 translate-x-[-4px] group-hover:translate-x-0
                     transition-all duration-200"
        >
          {item.label}
        </span>
      )}
    </li>
  );
}

/* ---------------- Section ---------------- */
function Section({ section, active, collapsed, onClick, showDivider }) {
  return (
    <div>
      {showDivider && (
        <div
          className="mx-3 my-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent"
          aria-hidden="true"
        />
      )}
      {!collapsed ? (
        <p className="px-4 pt-2 pb-2 text-[10px] font-bold tracking-[0.2em] text-slate-400/80 uppercase">
          {section.header}
        </p>
      ) : (
        <div className="py-1" aria-hidden="true" />
      )}
      <ul className="space-y-1 px-2">
        {section.items.map((item) => (
          <MenuItem
            key={item.id}
            item={item}
            active={active}
            collapsed={collapsed}
            onClick={onClick}
          />
        ))}
      </ul>
    </div>
  );
}

/* ---------------- Sidebar ---------------- */
export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [active, setActive] = useState("dashboard");

  return (
    <aside
      aria-label="Main navigation"
      className={[
        "relative h-screen flex flex-col",
        "transition-all duration-300 ease-in-out",
        collapsed ? "w-20" : "w-[260px]",
        // Gradient background — dark navy → indigo → violet (reduced blue)
        "bg-gradient-to-b from-[#0b0b1f] via-[#1a1340] to-[#2a1050]",
        // Glassmorphism + soft edges
        "backdrop-blur-xl border-r border-white/10",
        "shadow-[4px_0_30px_rgba(0,0,0,0.35)]",
        "rounded-r-2xl",
      ].join(" ")}
    >
      {/* Ambient glow */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 rounded-r-2xl overflow-hidden"
      >
        <div className="absolute -top-24 -left-10 w-64 h-64 bg-violet-600/20 blur-3xl rounded-full" />
        <div className="absolute bottom-0 -right-10 w-64 h-64 bg-fuchsia-600/15 blur-3xl rounded-full" />
      </div>

      {/* Header — logo icon only */}
      <div
        className={[
          "relative flex items-center px-4 py-5",
          collapsed ? "justify-center" : "justify-between",
        ].join(" ")}
      >
        <div
          className="flex items-center justify-center h-10 w-10 rounded-xl
                     bg-gradient-to-br from-violet-500 to-fuchsia-500
                     shadow-[0_0_20px_rgba(168,85,247,0.45)] ring-1 ring-white/15"
          aria-hidden="true"
        >
          <Sparkles className="h-5 w-5 text-white" />
        </div>

        {!collapsed && (
          <button
            onClick={() => setCollapsed(true)}
            aria-label="Collapse sidebar"
            className="flex items-center justify-center h-8 w-8 rounded-lg
                       text-slate-400 hover:text-white hover:bg-white/10
                       transition-all duration-200"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Divider under header */}
      <div className="mx-3 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      {/* Nav sections */}
      <nav
        className="relative flex-1 overflow-y-auto py-3 scrollbar-thin scrollbar-thumb-white/10"
        aria-label="Sidebar navigation"
      >
        {MENU_SECTIONS.map((section, idx) => (
          <Section
            key={section.header}
            section={section}
            active={active}
            collapsed={collapsed}
            onClick={setActive}
            showDivider={idx > 0}
          />
        ))}
      </nav>

      {/* Expand button when collapsed */}
      {collapsed && (
        <div className="relative p-3 flex justify-center">
          <button
            onClick={() => setCollapsed(false)}
            aria-label="Expand sidebar"
            className="flex items-center justify-center h-9 w-9 rounded-xl
                       bg-white/5 text-slate-300 hover:text-white hover:bg-white/10
                       ring-1 ring-white/10 transition-all duration-200"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Footer accent bar */}
      <div
        aria-hidden="true"
        className="relative h-1 w-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 rounded-br-2xl"
      />
    </aside>
  );
}

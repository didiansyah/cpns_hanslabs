import { cn } from "@/lib/format";
const variants: Record<string, string> = {
  default: "bg-primary text-primary-foreground",
  secondary: "bg-secondary text-secondary-foreground border border-border/60",
  destructive: "bg-destructive text-white",
  outline: "border border-border bg-background/60 text-foreground",
};
export function Badge({ className, variant = "default", ...props }: React.HTMLAttributes<HTMLSpanElement> & { variant?: string }) {
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className)} {...props} />;
}

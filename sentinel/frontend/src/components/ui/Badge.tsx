import React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-white",
  {
    variants: {
      variant: {
        default: "border-transparent bg-sky-50 text-sky-700 hover:bg-sky-100",
        secondary: "border-transparent bg-gray-100 text-gray-700 hover:bg-gray-200",
        destructive: "border-transparent bg-rose-50 text-rose-700 hover:bg-rose-100 shadow-sm",
        outline: "text-gray-700 border-gray-300",
        success: "border-transparent bg-emerald-50 text-emerald-700 hover:bg-emerald-100",
        warning: "border-transparent bg-amber-50 text-amber-700 hover:bg-amber-100",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }

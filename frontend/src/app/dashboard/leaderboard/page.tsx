"use client";
import { useState, useEffect } from "react";
import { apiGet } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Medal, Crown, Loader2 } from "lucide-react";

const MEDAL_COLORS = [
  { bg: "bg-amber-500/10", text: "text-amber-500", border: "border-amber-500/30" },
  { bg: "bg-gray-400/10", text: "text-gray-400", border: "border-gray-400/30" },
  { bg: "bg-orange-600/10", text: "text-orange-600", border: "border-orange-600/30" },
];

export default function LeaderboardPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet("/leaderboard").then((res) => {
      if (res.ok) setData(res.data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight font-serif">Leaderboard</h1>

      {/* Top 3 Podium */}
      {data.length >= 3 && (
        <div className="grid grid-cols-3 gap-3">
          {[1, 0, 2].map((idx) => {
            const d = data[idx];
            const medal = MEDAL_COLORS[idx];
            const isFirst = idx === 0;
            return (
              <Card key={idx} className={`border-border/50 ${isFirst ? "ring-1 ring-amber-500/20" : ""}`}>
                <CardContent className="p-4 text-center">
                  <div className={`mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full ${medal.bg} ${medal.border} border`}>
                    {isFirst ? (
                      <Crown className={`h-5 w-5 ${medal.text}`} />
                    ) : (
                      <Medal className={`h-5 w-5 ${medal.text}`} />
                    )}
                  </div>
                  <p className="font-semibold text-sm truncate">{d.name}</p>
                  <p className="text-2xl font-bold font-mono mt-1">{d.total}</p>
                  <div className="flex items-center justify-center gap-1.5 mt-2">
                    <Badge variant="secondary" className="text-[10px] px-1.5">TWK:{d.twk_score}</Badge>
                    <Badge variant="secondary" className="text-[10px] px-1.5">TIU:{d.tiu_score}</Badge>
                    <Badge variant="secondary" className="text-[10px] px-1.5">TKP:{d.tkp_score}</Badge>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Card className="border-border/50">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-serif">Top Peserta</CardTitle>
            {data.length > 0 && (
              <Badge variant="secondary" className="text-xs font-mono">{data.length} peserta</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : data.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Trophy className="h-10 w-10 text-muted-foreground/30 mb-3" />
              <p className="text-muted-foreground text-sm">Belum ada data.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {data.map((d, i) => {
                const medal = i < 3 ? MEDAL_COLORS[i] : null;
                return (
                  <div key={i} className={`flex items-center gap-4 p-3.5 border rounded-xl transition-colors hover:border-foreground/20 ${
                    medal ? `${medal.border} border` : "border-border/50"
                  }`}>
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold ${
                      medal ? `${medal.bg} ${medal.text}` : "bg-secondary text-muted-foreground"
                    }`}>
                      {medal ? (
                        i === 0 ? <Crown className="h-4 w-4" /> : <Medal className="h-4 w-4" />
                      ) : d.rank}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{d.name}</p>
                      <p className="text-xs text-muted-foreground">{d.study_days} hari belajar · {d.sim_count} simulasi</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold font-mono text-lg">{d.total}</p>
                      <div className="flex items-center gap-1">
                        <span className="text-[10px] text-muted-foreground">TWK:{d.twk_score}</span>
                        <span className="text-[10px] text-muted-foreground">TIU:{d.tiu_score}</span>
                        <span className="text-[10px] text-muted-foreground">TKP:{d.tkp_score}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

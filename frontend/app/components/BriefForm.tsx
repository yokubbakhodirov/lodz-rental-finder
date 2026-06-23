"use client";

interface Props {
  text: string;
  onChange: (text: string) => void;
  onSubmit: (brief: string) => void;
  disabled: boolean;
}

export const EXAMPLE_BRIEF =
  "Budget 2200 PLN, near tram, 2 rooms, Polesie or Widzew, good renovation, young family";

export default function BriefForm({ text, onChange, onSubmit, disabled }: Props) {
  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="text-xs tracking-widest text-orange-600 text-center mb-4">
        ● ŁÓDŹ RENTAL FINDER ●
      </div>
      <div className="bg-white rounded-2xl shadow-sm border border-orange-100 p-6">
        <div className="text-[11px] tracking-widest text-neutral-400 mb-2">
          › WRITE YOUR BRIEF — ENGLISH
        </div>
        <textarea
          className="w-full resize-none text-xl leading-relaxed outline-none text-neutral-800 placeholder:text-neutral-300"
          rows={3}
          maxLength={240}
          value={text}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
        />
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-neutral-100 text-xs text-neutral-400">
          <span>{text.length}/240 characters</span>
          <button
            onClick={() => onSubmit(text)}
            disabled={disabled || text.trim().length === 0}
            className="bg-orange-600 hover:bg-orange-700 disabled:bg-neutral-300 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors"
          >
            🚀 Start scan
          </button>
        </div>
      </div>
    </div>
  );
}

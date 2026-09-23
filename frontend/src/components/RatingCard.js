import React from 'react';

const BAND_CLASS = {
  Excellent: 'band-excellent',
  Good: 'band-good',
  Moderate: 'band-moderate',
  Poor: 'band-poor',
  Avoid: 'band-avoid',
};

function IngredientRow({ item }) {
  const sign = item.points > 0 ? '+' : '';
  return (
    <li className={`ingredient ingredient-${item.effect}`}>
      <span className="ingredient-name">{item.ingredient}</span>
      {item.effect !== 'neutral' && (
        <>
          <span className="ingredient-points">{sign}{item.points}</span>
          <span className="ingredient-reason">{item.reason}</span>
        </>
      )}
    </li>
  );
}

export default function RatingCard({ rating }) {
  const flagged = rating.ingredients.filter((i) => i.effect !== 'neutral');
  const neutral = rating.ingredients.filter((i) => i.effect === 'neutral');

  return (
    <section className="card">
      <div className="score-row">
        <div className={`score ${BAND_CLASS[rating.band]}`}>
          <span className="score-number">{rating.score}</span>
          <span className="score-band">{rating.band}</span>
        </div>
        <p className="score-maths">
          Starts at {rating.base_score}, {rating.penalty} for {rating.concerns} concern
          {rating.concerns === 1 ? '' : 's'}, +{rating.bonus} for {rating.benefits} beneficial
          ingredient{rating.benefits === 1 ? '' : 's'}
          {rating.bonus_capped && ' (bonus capped)'}.
        </p>
      </div>

      {flagged.length > 0 && (
        <ul className="ingredient-list">
          {flagged.map((item) => <IngredientRow key={item.ingredient} item={item} />)}
        </ul>
      )}

      {neutral.length > 0 && (
        <details>
          <summary>{neutral.length} other ingredients</summary>
          <p className="muted">{neutral.map((i) => i.ingredient).join(', ')}</p>
        </details>
      )}
    </section>
  );
}

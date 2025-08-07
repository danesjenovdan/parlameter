# How cards work

## File structure

### Naming

Each card has a `group` and a `method` (sometimes just called `name`), which when combined create a `cardName`.

For example:

- group: `person`
- method `basic-information`
- cardName: `person/basic-information`

### Location

For the build system to find a card you need to create a `card.vue` in the appropriate directory.

All the cards are stored in the [cards](../cards) folder, and subfolders based ond the `cardName`.

For example:

- [person/basic-information/card.vue](../cards/person/basic-information/card.vue)

### Required files

When creating a new card there are some required files:

- `card.vue` - The main entry point for the card when it gets built.
- `data.json` - API data used when developing the card.
- `state.json` - State used when developing the card.

Not strictly required while developing but could error when built:

- `_i18n/<lang>/<cardName>.yaml` - The locale file for the card. (You can use `yarn lint:locales` to check if any locale files are missing)

## Data

### Context data

Cards get external data when they are rendered. This is passed in as `contextData` and is available in the root card component as `this.$options.contextData`

It includes things like:

- `cardData` - API data from `parladata` for this particular id,
- `cardState` - Saved state from the card (like current tab or filter, usually used when embedding).
- `urls` - URLs to other parts of parlameter (like assets, site, data, ...)
- ...

### ! Be careful !

Some data that cards use is also given in the query parameters (for example id, locale, template). It is tempting to get this data using `window.location.search` - but preferably avoid using it, expect for when you are **absolutely sure** the `window` object will only be called on client side - otherwise all cards will crash!

If you need these parameters it's better to add them to the `contextData` object that is constructed in server/render-card.js.

### Format of `cardData`

```json
{
  "url": "<the actual url from when the data was fetched>",
  "id": "<id specified in the card>",
  // data fetched from the url
  "data": {
    "results": { ... }
  },
  // if there was any error fetching data, otherwise false
  "error": { message, error, statusCode, code } || false
};
```

### Common mixin

The top-most card component needs to import the [`common`](../cards/_mixins/common.js) mixin. This sets up some data required for the template render and imports the `card-wrapper` you need as the main card component, that creates the main card frame.

### `cardInfo` property

The root component can have a `cardInfo` property that is used to tell information to the templating engine later.

```js
cardInfo: {
  doubleWidth: true,
},
```

## State

### Analysis options

List of analysis IDs that can be used on misc/members:

- `demographics` - name, age, education, no. of mandates, group, ...

- `presence_votes` - how often each member was present on votings

- `number_of_questions` - how many questions / suggestions each member gave

- `mismatch_of_pg` - how many times did each member vote differently from their member group

- `working_bodies` - a list of working bodies each member is a part of

- analysis of transcripts:

  - `speeches_per_session` - average number of speeches each member gave per session

  - `spoken_words` - number of words each member spoke

#### List of analysis IDs that can be used on misc/groups:

- `seat_count` - how many seats does each group have

- `vote_attendance` - average presence on votings

- `number_of_questions` - how many questions / suggestions each group gave

- `number_of_amendments` - how many amendments each group gave

- `group_unity` - how differently do members of each group vote on average

- analysis of transcripts:

  - `vocabulary_size` - how rich vocabulary they use

class BadRequest extends Error {
  constructor (msg) {
    super(msg)
  }
}

module.exports = BadRequest
